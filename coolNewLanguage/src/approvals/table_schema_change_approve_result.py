import pandas as pd

from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class TableSchemaChangeApproveResult(ApproveResult):
    __slots__ = ('table_name', 'cols_added', 'dataframe', 'column_names')

    def __init__(self, table_name: str, cols_added: list[str], new_df: pd.DataFrame):
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(cols_added, list):
            raise TypeError("Expected cols_added to be a list")
        if not isinstance(new_df, pd.DataFrame):
            raise TypeError("Expected new_df to be a DataFrame")

        self.approve_result_type = ApproveResultType.TABLE_SCHEMA_CHANGE
        self.table_name = table_name
        self.cols_added = cols_added
        self.dataframe = new_df
        self.column_names = self.dataframe.columns.tolist()

        super().__init__()