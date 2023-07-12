from typing import Optional, Any

import sqlalchemy

from coolNewLanguage.src.cell import Cell


def verify_cell(cell: Cell,
                table: Optional[sqlalchemy.Table] = None,
                col_name: Optional[str] = None,
                row_id: Optional[int] = None,
                expected_type: Optional[type] = None,
                val: Optional[Any] = None) -> None:
    """
    Utility method for testing used to verify the fields of a cell
    Uses asserts, so doesn't return anything
    :param cell: The Cell to check
    :param table:
    :param col_name:
    :param row_id:
    :param expected_type:
    :param val:
    :return:
    """
    if not isinstance(cell, Cell):
        raise TypeError("Expected cell to be a Cell")

    if table is not None:
        assert cell.table == table

    if col_name is not None:
        assert cell.col_name == col_name

    if row_id is not None:
        assert cell.row_id == row_id

    if expected_type is not None:
        assert cell.expected_type == expected_type

    if val is not None:
        assert cell.val == val