from typing import Dict, Any

import sqlalchemy

from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME
from coolNewLanguage.src.tool import *
from typing import Type

class Row:
    """
    Represents a row in a table, which can be indexed into dictionary style using column names
    Acts as a wrapper class around the sqlalchemy Row class
    """
    def __init__(self, table: sqlalchemy.Table, sql_alchemy_row: sqlalchemy.Row):
        if not isinstance(sql_alchemy_row, sqlalchemy.Row):
            raise TypeError("Expected sql_alchemy_row to be a sqlalchemy Row")
        if not isinstance(table, sqlalchemy.Table):
            raise TypeError("Expected table to be a sqlalchemy Table")

        self.row_mapping = sql_alchemy_row._asdict()
        self.table = table
        self.row_id = self.row_mapping[DB_INTERNAL_COLUMN_ID_NAME]
        self.cell_mapping = {}

    def __getitem__(self, item) -> Cell:
        """
        Get an item in this row using a column name, returning a Cell
        If item is a ColumnSelectorComponent, then use the column name instead
        If is a ColumnSelectorComponent and has an expected type, cast to that
        :param item:
        :return:
        """
        col_name = item.emulated_column if hasattr(item, 'emulated_column') else item

        if col_name not in self.cell_mapping:
            val = self.row_mapping[col_name]
            expected_type = item.expected_val_type if hasattr(item, 'expected_val_type') else None
            self.cell_mapping[col_name] = Cell(
                table=self.table,
                col_name=col_name,
                row_id=self.row_id,
                expected_type=expected_type,
                val=val
            )

        return self.cell_mapping[col_name]

    def __setitem__(self, key, value):
        """Assign to a cell in this row, using key as the column name and value as the new value"""
        if key not in self.cell_mapping:
            self.cell_mapping[key] = Cell(table=self.table, col_name=key, row_id=self.row_id)

        cell = self.cell_mapping[key]
        cell.set(value)

    def keys(self):
        """Returns the column names of this row, which can be used to index into this row"""
        return self.row_mapping.keys()

    def __contains__(self, item):
        """Returns whether this row contains a certain column"""
        return item in self.row_mapping.keys()

    class RowIterator:
        """
        An iterator for a given row, which iterates over each value in that row
        """
        def __init__(self, table: sqlalchemy.Table, row_mapping: Dict[str, Any], row_id: int):
            if not isinstance(table, sqlalchemy.Table):
                raise TypeError("Expected table to be a sqlalchemy Table")
            if not isinstance(row_mapping, Dict):
                raise TypeError("Expected row_mapping to be a dict")
            if not all([isinstance(k, str) for k in row_mapping.keys()]):
                raise TypeError("Expected all the keys of row_mapping to be a string")

            self.table = table
            self.row_mapping = row_mapping
            self.col_names = row_mapping.keys()
            self.row_id = row_id

        def __iter__(self) -> 'RowIterator':
            return self

        def __next__(self) -> Cell:
            try:
                col_name = self.col_names.__next__()
            except StopIteration:
                raise StopIteration

            return Cell(table=self.table, col_name=col_name, row_id=self.row_id, val=self.row_mapping[col_name])

    def __iter__(self):
        """Iterate over the cells in this row"""
        return Row.RowIterator(table=self.table, row_mapping=self.row_mapping, row_id=self.row_id)

    def asType(self, type:type[CNLType])->CNLType:
        return type(backing_row=self)
    
    def link(self, to:Any, on:"Link"):
        from coolNewLanguage.src.row import Row
        from coolNewLanguage.src.util.db_utils import link_create
        from coolNewLanguage.src.stage import process

        link_id = on._hls_internal_link_id

        src_row_id:int = self.row_id
        dst_row_id:int
        dst_table:str
        if (isinstance(to, Row)):
            to:Row
            dst_row_id = to.row_id
            dst_table = to.table.name
        elif (isinstance(to, CNLType)):
            to:CNLType
            dst_row_id = to.__hls_backing_row.row_id
            dst_table = to.__hls_backing_row.table.name
        else:
            raise TypeError("Unexpected link target type")

        link = link_create(process.running_tool, link_id, src_row_id, dst_table, dst_row_id)
        print("Created link", link)