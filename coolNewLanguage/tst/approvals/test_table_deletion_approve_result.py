from unittest.mock import Mock, patch, MagicMock

import pandas as pd
import pytest

from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.approvals.table_deletion_approve_result import TableDeletionApproveResult


class TestTableDeletionApproveResult:

    TABLE_NAME = "table_name"
    MOCK_HTML = "<html>mock</html>"

    @patch("coolNewLanguage.src.approvals.table_deletion_approve_result.ApproveResult.__init__")
    def test_TableDeletionApproveResult_happy_path(self, mock_ApproveResult_init: MagicMock):
        # Do
        # Mock the dataframe to pass
        mock_dataframe = Mock(spec=pd.DataFrame, to_html=Mock(return_value=self.MOCK_HTML))
        table_deletion_approve_result = TableDeletionApproveResult(self.TABLE_NAME, mock_dataframe)

        # Check
        assert table_deletion_approve_result.table_name == self.TABLE_NAME
        assert table_deletion_approve_result.dataframe_html == self.MOCK_HTML
        mock_ApproveResult_init.assert_called_once()
        assert table_deletion_approve_result.approve_result_type == ApproveResultType.TABLE_DELETION

    def test_TableDeletionApproveResult_non_string_table_name(self):
        # Do/Check
        with pytest.raises(TypeError, match="Expected table_name to be a string"):
            TableDeletionApproveResult(Mock(), Mock())

    def test_TableDeletionApproveResult_non_dataframe_dataframe(self):
        # Do/Check
        with pytest.raises(TypeError, match="Expected dataframe to be a DataFrame"):
            TableDeletionApproveResult(self.TABLE_NAME, Mock())