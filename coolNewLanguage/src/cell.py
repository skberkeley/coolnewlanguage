from typing import Optional, Any

import sqlalchemy

from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util.db_utils import get_cell_value, update_cell


class Cell:
    """
    Represents a single cell within a sqlalchemy Table
    Used to support updates to an existing table, as well as iteration over a column
    """
    def __init__(self, table: sqlalchemy.Table, col_name: str, row_id: int, expected_type: Optional[type] = None,
                 val: Optional[Any] = None):
        """
        Initialize the cell, issuing a query if val is None to get the value from the passed table
        :param table: The sqlalchemy table containing the cell
        :param col_name: The name of the containing column
        :param row_id: The row id of the cell
        :param expected_type: The expected type of the cell's value
        :param val: The value of the cell. If None, a query is issued to get the value
        """
        if not isinstance(table, sqlalchemy.Table):
            raise TypeError("Expected table to be a sqlalchemy table")
        if not isinstance(col_name, str):
            raise TypeError("Expected col_name to be a string")
        if not isinstance(row_id, int):
            raise TypeError("Expected row_id to be an int")
        if expected_type is not None and not isinstance(expected_type, type):
            raise TypeError("Expected expected_type to be a type")

        self.table = table
        self.col_name = col_name
        self.row_id = row_id
        self.expected_type = expected_type

        if val is not None:
            self.val = val
        else:
            self.val = expected_type(get_cell_value(process.running_tool, table, col_name, row_id))

    def __str__(self) -> str:
        return str(self.val)

    def __add__(self, other):
        return self.expected_type(self.val) + other

    def set(self, value: Any):
        """
        Update this cell's value
        Overwrites data in the database by issuing an update statement
        :param value:
        :return:
        """
        update_cell(tool=process.running_tool, table=self.table, column_name=self.col_name, row_id=self.row_id,
                    value=value)

    def __lshift__(self, other: Any):
        """
        Set the value of this cell to other, executing an update statement too
        :param other:
        :return:
        """
        self.set(other)

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.val == other.val
        return self.val == other
