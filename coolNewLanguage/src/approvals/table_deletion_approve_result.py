import pandas as pd

from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType


class TableDeletionApproveResult(ApproveResult):
    __slots__ = ('table_name', 'dataframe', 'dataframe_html')

    def __init__(self, table_name: str, dataframe: pd.DataFrame):
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Expected dataframe to be a DataFrame")

        self.table_name = table_name
        self.dataframe_html = dataframe.to_html(index=False, border=0, justify="left")

        super().__init__()
        self.approve_result_type = ApproveResultType.TABLE_DELETION
