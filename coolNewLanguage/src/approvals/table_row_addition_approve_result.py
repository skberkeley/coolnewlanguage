import pandas as pd

from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class TableRowAdditionApproveResult(ApproveResult):
    __slots__ = ('table_name', 'rows_added', 'dataframe', 'column_names')

    def __init__(self, table_name: str, rows_added: list[int], new_df: pd.DataFrame):
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(rows_added, list):
            raise TypeError("Expected rows_added to be a list")
        if not isinstance(new_df, pd.DataFrame):
            raise TypeError("Expected new_df to be a DataFrame")

        self.approve_result_type = ApproveResultType.TABLE_ROW_ADDITION
        self.table_name = table_name
        self.rows_added = set(rows_added)
        self.dataframe = new_df
        self.column_names = self.dataframe.columns.tolist()

        print(f"approve result columns: {self.column_names}")

        super().__init__()
