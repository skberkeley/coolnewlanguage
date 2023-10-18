from typing import Optional, Any

import sqlalchemy

from coolNewLanguage.src.exceptions.CNLError import raise_type_casting_error
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util.db_utils import get_cell_value, update_cell


class Cell:
    """
    Represents a single cell within a sqlalchemy Table
    Used to support updates to an existing table, as well as iteration over a column
    Even though Cell has an expected_type field, the responsibility of casting the value to that type rests on consumers
    of the value
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
            raise TypeError("Expected table to be a sqlalchemy Table")
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

        if val is None:
            val = get_cell_value(process.running_tool, table, col_name, row_id)

        if expected_type is not None:
            try:
                self.val = expected_type(val)
            except Exception as e:
                raise_type_casting_error(val, expected_type, e)
        else:
            self.val = val

    def __str__(self) -> str:
        return str(self.get_val())

    def __add__(self, other):
        return self.expected_type(self.val) + other

    def set(self, value: Any):
        """
        Update this cell's value
        Overwrites data in the database by issuing an update statement
        :param value:
        :return:
        """
        if self.expected_type is not None:
            try:
                value = self.expected_type(value)
            except Exception as e:
                raise_type_casting_error(value, self.expected_type, e)
        self.val = value

    def __lshift__(self, other: Any):
        """
        Set the value of this cell to other, executing an update statement too
        :param other:
        :return:
        """
        self.set(other)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Cell):
            return self.val == other.get_val()
        return self.val == other

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, Cell):
            return self.val * other.get_val()
        return self.val * other

    def get_val(self) -> Any:
        """
        Returns this cell's value for consumption by other objects
        Tries to cast the value to the expected type before returning
        :return:
        """
        if self.expected_type is not None:
            try:
                ret = self.expected_type(self.val)
            except Exception as e:
                raise_type_casting_error(self.val, self.expected_type, e)
        return self.val