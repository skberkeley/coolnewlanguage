import pandas as pd

from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class TableApproveResult(ApproveResult):
    __slots__ = ('column_names', 'dataframe', 'table_name')

    def __init__(self, table_name: str, dataframe: pd.DataFrame):
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Expected dataframe to be a pandas DataFrame")

        super().__init__()
        self.approve_result_type = ApproveResultType.TABLE
        self.dataframe = dataframe
        self.table_name = table_name

        self.column_names = self.dataframe.columns.tolist()
