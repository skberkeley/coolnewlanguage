from unittest.mock import patch, MagicMock, Mock

import pandas as pd
import pytest

from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult


class TestTableApproveResult:

    TABLE_NAME = 'table_name'
    COLUMN_NAMES = ['column1', 'column2']

    @patch('coolNewLanguage.src.approvals.table_approve_result.ApproveResult.__init__')
    def test_init_happy_path(self, mock_approve_result_init: MagicMock):
        # Setup
        mock_dataframe = Mock(spec=pd.DataFrame, columns=Mock(tolist=Mock(return_value=self.COLUMN_NAMES)))

        # Do
        table_approve_result = TableApproveResult(self.TABLE_NAME, mock_dataframe)

        # Check
        mock_approve_result_init.assert_called_once()
        assert table_approve_result.approve_result_type == ApproveResultType.TABLE
        assert table_approve_result.dataframe == mock_dataframe
        assert table_approve_result.table_name == self.TABLE_NAME
        assert table_approve_result.column_names == self.COLUMN_NAMES

    def test_init_non_string_table_name(self):
        # Do/Check
        with pytest.raises(TypeError, match="Expected table_name to be a string"):
            TableApproveResult(Mock(), Mock(spec=pd.DataFrame))

    def test_init_non_dataframe_dataframe(self):
        # Do/Check
        with pytest.raises(TypeError, match="Expected dataframe to be a pandas DataFrame"):
            TableApproveResult(self.TABLE_NAME, Mock())
