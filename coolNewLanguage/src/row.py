from typing import Any, Union, Optional

import sqlalchemy

from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.link_utils import get_link_id, register_new_link
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME


class Row:
    """
    Represents a row in a table, which can be indexed into dictionary style using column names
    Acts as a wrapper class around the sqlalchemy Row class
    Assumed to have a database-synced view of data

    Attributes:
        row_mapping:
            The mapping representation of the underlying sqlalchemy Row
            Maps from column names to cell values
            Contains an up-to-date view of the database's values
        table:
            The underlying sqlalchemy Table which this Row is a member of
        row_id:
            The id of this Row in the underlying Table
        cell_mapping:
            A mapping from column names to Cell instances
            cell_mapping keys are a subset of row_mapping's keys
            Cell values may be more updated than row_mapping and the database's values
    """
    def __init__(self, table: sqlalchemy.Table, sqlalchemy_row: sqlalchemy.Row):
        if not isinstance(table, sqlalchemy.Table):
            raise TypeError("Expected table to be a sqlalchemy Table")
        if not isinstance(sqlalchemy_row, sqlalchemy.Row):
            raise TypeError("Expected sqlalchemy_row to be a sqlalchemy Row")

        self.row_mapping: dict[str, Any] = sqlalchemy_row._asdict()
        self.table: sqlalchemy.Table = table
        self.row_id: int = self.row_mapping[DB_INTERNAL_COLUMN_ID_NAME]
        self.cell_mapping: dict[str, Cell] = {}

    def __getitem__(self, item: str) -> Cell:
        """
        Get an item in this row using a column name, returning a Cell
        If item is a ColumnSelectorComponent, then use the column name instead
        If is a ColumnSelectorComponent and has an expected type, add the expected type to the returned Cell
        :param item: Either a string or ColumnSelectorComponent containing the column name for which the corresponding
                     Cell is being requested
        :return: A Cell containing the value corresponding to the passed column
        """
        if not isinstance(item, str):
            raise TypeError("Expected item to be a string")

        col_name = item

        # if the desired item does not yet exist as a Cell, create a new Cell, adding it to cell_mapping
        if col_name not in self.cell_mapping:
            val = self.row_mapping[col_name]
            self.cell_mapping[col_name] = Cell(
                table=self.table,
                col_name=col_name,
                row_id=self.row_id,
                val=val
            )

        cell = self.cell_mapping[col_name]

        return self.cell_mapping[col_name]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Assign to a cell in this row, using key as the column name and value as the new value
        :param key: The column name to assign to
        :param value: The value to assign
        :return:
        """
        if not isinstance(key, str):
            raise TypeError("Expected key to be a string")

        # Check that key is a valid column name
        if key not in self.row_mapping:
            raise ValueError(f"Key {key} is not a valid column name")

        # If a cell hasn't been created yet, instantiate it
        if key not in self.cell_mapping:
            # Pass in old val, else Cell makes database call to retrieve val, which will be updated soon anyway
            self.cell_mapping[key] = Cell(
                table=self.table,
                col_name=key,
                row_id=self.row_id,
                val=self.row_mapping[key]
            )

        cell = self.cell_mapping[key]
        cell.set(value)

    def keys(self):
        """Returns the column names of this row, which can be used to index into this row"""
        return self.row_mapping.keys()

    def __contains__(self, item) -> bool:
        """Returns whether this row contains a certain column"""
        return item in self.row_mapping.keys()

    def save(self, get_user_approvals: bool = False):
        """
        Saves the current state of this row to the database, by updating values where the cell values differ from the
        values in row_mapping.
        :param get_user_approvals: Whether to get user approvals before saving changes to the database.
        :return:
        """
        # Update row_mapping
        for col_name, cell in self.cell_mapping.items():
            self.row_mapping[col_name] = cell.get_val()

        if get_user_approvals:
            from coolNewLanguage.src.approvals.row_approve_result import RowApproveResult
            table_name = self.table.name
            approve_result = RowApproveResult(row=self.row_mapping, table_name=table_name, is_new_row=False)
            process.approve_results.append(approve_result)
            return

        # Create an update statement
        id_column = self.table.c[DB_INTERNAL_COLUMN_ID_NAME]
        stmt = sqlalchemy.update(self.table).where(id_column == self.row_id).values(self.row_mapping)

        # Execute the update statement
        tool: Tool = process.running_tool
        with tool.db_engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    class RowIterator:
        """
        An iterator for a given row, which iterates over each value in that row
        Attributes:
            row:
                The underlying row to use to get values
            col_names:
                The column names of this row
        """
        def __init__(self, row: 'Row'):
            self.row = row
            self.col_names_iterator = row.row_mapping.keys().__iter__()

        def __next__(self) -> Cell:
            try:
                col_name = self.col_names_iterator.__next__()
            except StopIteration:
                raise StopIteration
            # take advantage of row's __getitem__, which will also update cell mapping
            return self.row[col_name]

    def __iter__(self):
        """Iterate over the cells in this row"""
        return Row.RowIterator(row=self)

    def cast_to_type(self, cnl_type: type['CNLType']) -> 'CNLType':
        from coolNewLanguage.src.cnl_type.cnl_type import CNLType
        """
        Returns an instance of the passed CNLType with this row as the underlying backing row.
        :param cnl_type: The CNLType subclass to return an instance of
        :return:
        """
        if not issubclass(cnl_type, CNLType):
            raise TypeError("Expected cnl_type to be a subclass of CNLType")

        return CNLType.from_row(cnl_type=cnl_type, row=self)

    def link(self, link_dst: Union['Row', 'CNLType'], link_metatype: 'LinkMetatype', get_user_approvals: bool = False) \
            -> Optional[Link]:
        """
        Links this Row to link_dst, which is either another Row or a CNLType instance. The resulting link will be of the
        passed metatype. First checks to see if a matching link already exists before trying to create it. Returns the
        id of the link. If not handling_post, does nothing and returns None instead.
        :param link_dst: The destination of the link to be created.
        :param link_metatype: The metatype of the link to be created.
        :param get_user_approvals: Whether to get user approvals before creating the link.
        :return:
        """
        from coolNewLanguage.src.stage import process
        from coolNewLanguage.src.cnl_type.cnl_type import CNLType
        from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype

        if not isinstance(link_dst, Row) and not isinstance(link_dst, CNLType):
            raise TypeError("Expected link_dst to be a Row or a CNLType instance")
        if not isinstance(link_metatype, LinkMetatype):
            raise TypeError("Expected link_metatype to be a Link")

        if not process.handling_post:
            return None

        if isinstance(link_dst, CNLType) and link_dst._hls_backing_row is None:
            return None

        tool = process.running_tool
        link_meta_id = link_metatype.get_link_meta_id()
        src_table_name = self.table.name
        src_row_id = self.row_id
        dst_table_name: str
        dst_row_id: int

        if isinstance(link_dst, Row):
            dst_table_name = link_dst.table.name
            dst_row_id = link_dst.row_id
        else:
            link_dst: CNLType
            dst_table_name = link_dst._hls_backing_row.table.name
            dst_row_id = link_dst._hls_backing_row.row_id

        link_id = get_link_id(
            tool=tool,
            link_meta_id=link_meta_id,
            src_table_name=src_table_name,
            src_row_id=src_row_id,
            dst_table_name=dst_table_name,
            dst_row_id=dst_row_id
        )

        if link_id is not None:
            return Link(link_meta_id, link_id, src_table_name, src_row_id, dst_table_name, dst_row_id)

        if get_user_approvals:
            from coolNewLanguage.src.approvals.link_approve_result import LinkApproveResult
            link = Link(link_meta_id, None, src_table_name, src_row_id, dst_table_name, dst_row_id)
            approve_result = LinkApproveResult(link=link)
            process.approve_results.append(approve_result)
            return link

        return register_new_link(
            tool=tool,
            link_meta_id=link_meta_id,
            src_table_name=src_table_name,
            src_row_id=src_row_id,
            dst_table_name=dst_table_name,
            dst_row_id=dst_row_id
        )
