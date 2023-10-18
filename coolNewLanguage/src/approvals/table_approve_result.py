import sqlalchemy

from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class TableApproveResult(ApproveResult):
    __slots__ = ('column_names', 'rows', 'sqlalchemy_table', 'table_name')

    def __init__(self, table: list[list], table_name: str, sqlalchemy_table: sqlalchemy.Table):
        if not isinstance(table, list):
            raise TypeError("Expected table to be a list")
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        # validate table
        if not all(isinstance(row, list) for row in table):
            raise TypeError("Expected each element of table to be a list")
        if len(table) == 0:
            raise ValueError("Expected table to have at least one row")
        if not all(len(row) == len(table[0]) for row in table[1:]):
            raise ValueError("Expected each row of table to have the same number of columns")

        super().__init__()
        self.approve_result_type = ApproveResultType.TABLE
        self.sqlalchemy_table = sqlalchemy_table
        self.table_name = table_name

        # get column names
        self.column_names = table[0]

        # get rows
        self.rows = table[1:]
