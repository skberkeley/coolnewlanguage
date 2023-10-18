from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class RowApproveResult(ApproveResult):
    """
    A class representing an approval result for a row being appended to an existing table.
    :param row: A dictionary mapping column names to values in the row
    :param table_name: The name of the table the row is being appended to
    """
    __slots__ = ('row', 'table_name', 'is_new_row')

    def __init__(self, row: dict, table_name: str, is_new_row: bool):
        if not isinstance(row, dict):
            raise TypeError("Expected row to be a dictionary")
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(is_new_row, bool):
            raise TypeError("Expected is_new_row to be a boolean")

        super().__init__()

        self.approve_result_type = ApproveResultType.ROW

        self.row = row
        self.table_name = table_name
        self.is_new_row = is_new_row