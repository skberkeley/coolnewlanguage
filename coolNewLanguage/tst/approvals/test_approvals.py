import asyncio
from unittest.mock import patch, Mock, MagicMock, call

import pytest
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.approvals import approvals
from coolNewLanguage.src.approvals.approvals import get_user_approvals
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
from coolNewLanguage.src.approvals.table_deletion_approve_result import TableDeletionApproveResult
from coolNewLanguage.src.exceptions.CNLError import CNLError


class TestApprovals:

    CURR_STAGE_URL = 'curr_stage_url'

    @patch('coolNewLanguage.src.approvals.approvals.Stage')
    @patch('coolNewLanguage.src.approvals.approvals.TableApproveResult')
    @patch('coolNewLanguage.src.approvals.approvals.TableDeletionApproveResult')
    @patch('coolNewLanguage.src.approvals.approvals.process')
    @patch('coolNewLanguage.src.approvals.approvals.config')
    def test_get_user_approvals_handling_post_happy_path(
            self,
            mock_config: MagicMock,
            mock_process: MagicMock,
            mock_TableDeletionApproveResult: MagicMock,
            mock_TableApproveResult: MagicMock,
            mock_Stage: MagicMock
    ):
        # Setup
        # Set config.building_template to False
        mock_config.building_template = False
        # Set process.handling_post to True
        mock_process.handling_post = True
        # Mock the jinja template
        mock_template = Mock(globals=MagicMock())
        mock_process.running_tool.jinja_environment.get_template.return_value = mock_template
        # Mock process.curr_stage_url
        mock_process.curr_stage_url = self.CURR_STAGE_URL
        # Clear approve_results
        approvals.approve_results = []
        # Mock tool.tables._tables_to_delete
        mock_process.running_tool.tables._tables_to_delete = {'table1', 'table2'}
        # Mock the TableDeletionApproveResult constructor
        mock_table_deletion_approve_results = [Mock(), Mock()]
        mock_TableDeletionApproveResult.side_effect = mock_table_deletion_approve_results
        # Mock tool.get_table_dataframe
        mock_dataframes = {'table1': Mock(), 'table2': Mock()}
        mock_process.running_tool._get_table_dataframe.side_effect = lambda table: mock_dataframes[table]
        # Mock tool.tables._tables_to_save
        mock_tables_to_save = {'table3': Mock(), 'table4': Mock()}
        mock_process.running_tool.tables._tables_to_save = mock_tables_to_save
        # Mock the TableApproveResult constructor
        mock_table_approve_results = [Mock(), Mock()]
        mock_TableApproveResult.side_effect = mock_table_approve_results
        # Mock template.render
        mock_rendered_template = Mock()
        mock_template.render.return_value = mock_rendered_template

        # Do
        get_user_approvals()

        # Check
        # Check that get_template was called with the correct argument
        mock_process.running_tool.jinja_environment.get_template.assert_called_once_with(
            name=consts.APPROVAL_PAGE_TEMPLATE_FILENAME
        )
        # Check that the template globals were set correctly
        mock_template.globals.__setitem__.assert_called_once_with('ApproveResultType', ApproveResultType)
        # Check that the TableDeletionApproveResults were constructed correctly
        mock_TableDeletionApproveResult.assert_has_calls(
            [call('table1', mock_dataframes['table1']), call('table2', mock_dataframes['table2'])],
            any_order=True
        )
        # Check that the TableApproveResults were constructed correctly
        mock_TableApproveResult.assert_has_calls(
            [call('table3', mock_tables_to_save['table3']), call('table4', mock_tables_to_save['table4'])],
            any_order=True
        )
        # Check that the approve_results were constructed correctly
        expected_approve_results = mock_table_deletion_approve_results + mock_table_approve_results
        assert approvals.approve_results == expected_approve_results
        # Check that the template was rendered correctly
        mock_template.render.assert_called_once_with(
            approve_results=expected_approve_results,
            form_action=f'/{self.CURR_STAGE_URL}/approve',
            form_method='post',
            form_enctype='multipart/form-data'
        )
        # Check that the rendered template was set correctly
        assert mock_Stage.approvals_template == mock_rendered_template

        approvals.approve_results = []

    @patch('coolNewLanguage.src.approvals.approvals.process')
    @patch('coolNewLanguage.src.approvals.approvals.config')
    def test_get_user_approvals_building_template_happy_path(self, mock_config: Mock, mock_process: Mock):
        # Setup
        # Clear approve_results
        approvals.approve_results = []
        # Set config.building_template to True
        mock_config.building_template = True

        # Do
        with pytest.raises(CNLError, match="get_user_approvals was called in an unexpected place. Did you forget to check if user input was received?"):
            get_user_approvals()

        # Check
        # Check that approve_results was not modified
        assert approvals.approve_results == []

    RESULTS_TITLE = 'results_title'

    @patch('coolNewLanguage.src.approvals.approvals.web.Response')
    @patch('coolNewLanguage.src.approvals.approvals.ApproveResult')
    @patch('coolNewLanguage.src.approvals.approvals.Stage')
    @patch('coolNewLanguage.src.approvals.approvals.results')
    @patch('coolNewLanguage.src.approvals.approvals.handle_table_deletion_approve_result')
    @patch('coolNewLanguage.src.approvals.approvals.handle_table_approve_result')
    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_approval_handler_cached_results_happy_path(
            self,
            mock_process: MagicMock,
            mock_handle_table_approve_result: MagicMock,
            mock_handle_table_deletion_approve_result: MagicMock,
            mock_results: MagicMock,
            mock_Stage: MagicMock,
            mock_ApproveResult: MagicMock,
            mock_Response: MagicMock
    ):
        # Setup
        # Mock request
        mock_request = Mock(spec=web.Request)
        # Mock approve_results
        approvals.approve_results = [Mock(spec=TableDeletionApproveResult), Mock(spec=TableApproveResult)]
        # Mock process.cached_show_results and process.cached_show_results_title
        mock_cached_result = Mock()
        mock_process.cached_show_results = [mock_cached_result]
        mock_process.cached_show_results_title = self.RESULTS_TITLE
        # Mock Stage.results_template
        mock_results_template = Mock()
        mock_Stage.results_template = mock_results_template
        # Mock returned Response
        mock_response_instance = Mock()
        mock_Response.return_value = mock_response_instance

        # Do
        response = asyncio.run(approvals.approval_handler(mock_request))

        # Check
        # Check that request.post was called
        mock_request.post.assert_called_once()
        # Check that handle_table_deletion_approve_result was called with the correct argument
        mock_handle_table_deletion_approve_result.assert_called_once_with(approvals.approve_results[0])
        # Check that handle_table_approve_result was called with the correct argument
        mock_handle_table_approve_result.assert_called_once_with(approvals.approve_results[1])
        # Check that show_results was called with the correct arguments
        mock_results.show_results.assert_called_once_with(mock_cached_result, results_title=self.RESULTS_TITLE)
        # Check that Stage.results_template was reset to None
        assert mock_Stage.results_template is None
        # Check that the relevant values in process were reset
        assert not mock_process.handling_user_approvals
        assert mock_process.approve_results == []
        assert mock_process.curr_stage_url == ''
        assert mock_process.approval_post_body is None
        assert mock_process.cached_show_results == []
        assert mock_process.cached_show_results_title == ''
        assert mock_ApproveResult.num_approve_results == 0
        # Assert that process.running_tool.tables._tables_to_delete was cleared
        mock_process.running_tool.tables._tables_to_delete.clear.assert_called_once()
        # Verify returned response is as expected
        assert response == mock_response_instance
        mock_Response.assert_called_once_with(body=mock_results_template, content_type=consts.AIOHTTP_HTML)

        approvals.approve_results = []

    # Patch handle_result functions so they're not actually called
    @patch('coolNewLanguage.src.approvals.approvals.handle_table_deletion_approve_result')
    # Patch ApproveResult so that no stateful changes are made
    @patch('coolNewLanguage.src.approvals.approvals.ApproveResult')
    # Patch process so that no stateful changes are made
    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_approval_handler_no_cached_results_happy_path(
            self,
            mock_process: MagicMock,
            mock_ApproveResult: MagicMock,
            mock_handle_table_deletion_approve_result: MagicMock
    ):
        # Setup
        # Set process.cached_show_results to an empty list
        mock_process.cached_show_results = []

        # Do/Check
        with pytest.raises(web.HTTPFound) as e:
            asyncio.run(approvals.approval_handler(Mock(spec=web.Request)))
            assert e.location == '/'

    def test_approval_handler_non_web_request_request(self):
        # Do/Check
        with pytest.raises(TypeError, match="Expected request to be an aiohttp web.Request"):
            asyncio.run(approvals.approval_handler(Mock()))

    # Patch process so that no stateful changes are made
    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_approval_handler_unrecognized_approve_result(self, mock_process: MagicMock):
        # Setup
        approvals.approve_results = [Mock()]

        # Do/Check
        with pytest.raises(ValueError, match="Unknown ApproveResult type"):
            asyncio.run(approvals.approval_handler(Mock(spec=web.Request)))

    TABLE_APPROVE_RESULT_ID = '0'
    TABLE_APPROVE_RESULT_TABLE_NAME = 'table_approve_result_table_name'

    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_handle_table_approve_result_happy_path(self, mock_process: MagicMock):
        # Setup
        # Mock a dataframe
        mock_iterrows_iterator = iter([(0, None), (1, None), (2, None)])
        mock_dataframe = Mock(iterrows=Mock(return_value=mock_iterrows_iterator))
        mock_process.approval_post_body = {
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_0': 'approve',
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_1': 'reject',
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_2': 'approve'
        }
        # Mock the filtered dataframe
        mock_filtered_dataframe = Mock()
        mock_dataframe.loc = MagicMock(__getitem__=Mock(return_value=mock_filtered_dataframe))
        # Mock the TableApproveResult
        mock_table_approve_result = Mock(
            dataframe=mock_dataframe,
            id=self.TABLE_APPROVE_RESULT_ID,
            table_name=self.TABLE_APPROVE_RESULT_TABLE_NAME
        )

        # Do
        approvals.handle_table_approve_result(mock_table_approve_result)

        # Check
        expected_approved_rows = [0, 2]
        mock_dataframe.loc.__getitem__.assert_called_once_with(expected_approved_rows)

        mock_process.running_tool.tables._save_table.assert_called_once_with(
            self.TABLE_APPROVE_RESULT_TABLE_NAME,
            mock_filtered_dataframe
        )

    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_handle_table_approve_result_no_approved_rows(self, mock_process: MagicMock):
        # Setup
        # Mock a dataframe
        mock_iterrows_iterator = iter([(0, None), (1, None), (2, None)])
        mock_dataframe = Mock(iterrows=Mock(return_value=mock_iterrows_iterator))
        mock_process.approval_post_body = {
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_0': 'reject',
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_1': 'reject',
            f'approve_{self.TABLE_APPROVE_RESULT_ID}_2': 'reject'
        }
        # Mock the TableApproveResult
        mock_table_approve_result = Mock(
            dataframe=mock_dataframe,
            id=self.TABLE_APPROVE_RESULT_ID,
        )

        # Do
        approvals.handle_table_approve_result(mock_table_approve_result)

        # Check
        mock_process.running_tool.tables._save_table.assert_not_called()

    TABLE_DELETE_APPROVE_RESULT_ID = 'table_delete_approve_result_id'
    TABLE_DELETE_TABLE_NAME = 'table_delete_table_name'

    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_handle_table_deletion_approve_result_approved_happy_path(self, mock_process: MagicMock):
        # Setup
        # Mock process.approval_post_body
        mock_process.approval_post_body = {f'approve_{self.TABLE_DELETE_APPROVE_RESULT_ID}': 'approve'}

        # Do
        # Mock a TableDeletionApproveResult
        mock_table_approve_result = Mock(
            id=self.TABLE_DELETE_APPROVE_RESULT_ID,
            table_name=self.TABLE_DELETE_TABLE_NAME
        )
        approvals.handle_table_deletion_approve_result(mock_table_approve_result)

        # Check
        mock_process.running_tool.tables._delete_table.assert_called_once_with(self.TABLE_DELETE_TABLE_NAME)

    @patch('coolNewLanguage.src.approvals.approvals.process')
    def test_handle_table_deletion_approve_result_rejected_happy_path(self, mock_process: MagicMock):
        # Setup
        # Mock process.approval_post_body
        mock_process.approval_post_body = {f'approve_{self.TABLE_DELETE_APPROVE_RESULT_ID}': 'reject'}

        # Do
        # Mock a TableDeletionApproveResult
        mock_table_approve_result = Mock(id=self.TABLE_DELETE_APPROVE_RESULT_ID)
        approvals.handle_table_deletion_approve_result(mock_table_approve_result)

        # Check
        mock_process.running_tool.tables._delete_table.assert_not_called()

