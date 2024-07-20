from unittest.mock import patch, Mock, MagicMock, call

import jinja2
import pytest
import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.stage.results import show_results, result_template_of_sql_alch_table, Result


class TestResults:
    LABEL = "Drink me"
    TITLE = "BIG OL' TABLE"
    RESULT_HTML = "<totally_html>"
    COL_NAME1 = "First Name"
    COL_NAME2 = "Last Name"

    @patch('coolNewLanguage.src.stage.results.result_template_of_value')
    @patch('coolNewLanguage.src.stage.results.Stage')
    @patch('coolNewLanguage.src.stage.results.process')
    def test_show_results_happy_path(
            self,
            mock_process: MagicMock,
            mock_Stage: MagicMock,
            mock_result_template_of_value: MagicMock
    ):
        # Setup
        # Set process.handling_post to True so show_results doesn't return early
        mock_process.handling_post = True
        # Mock some values
        values = [results.Result(Mock()), (Mock(), TestResults.LABEL), Mock()]
        # Set Stage.approvals_template to None so show_results doesn't cache the results
        mock_Stage.approvals_template = None
        # Mock get_template
        mock_get_template = mock_process.running_tool.jinja_environment.get_template
        mock_template = Mock()
        mock_get_template.return_value = mock_template

        # Do
        show_results(*values)

        # Check
        # Check that result_template_of_value has the expected calls
        mock_result_template_of_value.assert_has_calls([call(values[0].value), call(values[1][0]), call(values[2])])
        # Check that get_template was called as expected
        mock_get_template.assert_called_with(name=consts.STAGE_RESULTS_TEMPLATE_FILENAME)
        # Check that template.render was called
        mock_template.render.assert_called_once()
        # Check that its return value was set on Stage
        assert mock_Stage.results_template == mock_template.render.return_value

    def test_show_results_non_string_results_title(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected results_title to be a string"):
            show_results(results_title=Mock())

    @patch('coolNewLanguage.src.stage.results.Stage')
    @patch('coolNewLanguage.src.stage.results.process')
    def test_show_results_not_handling_post(self, mock_process: MagicMock, mock_Stage: MagicMock):
        # Setup
        # Set to handling_post and handling_user_approvals to False so show_results returns early
        mock_process.handling_post = False
        mock_process.handling_user_approvals = False

        # Do
        show_results(results_title=TestResults.TITLE)

        # Check
        # Check that Stage.results_template is still None
        assert mock_Stage.results_template is None

    @patch('coolNewLanguage.src.stage.results.Stage')
    @patch('coolNewLanguage.src.stage.results.process')
    def test_show_results_approvals_set(self, mock_process: MagicMock, mock_Stage: MagicMock):
        # Setup
        mock_process.handling_post = True
        # Set Stage.approvals_template so show_results caches the results
        mock_Stage.approvals_template = Mock()
        # Set mock_Stage.results_template to None so we can check that it doesn't get set
        mock_Stage.results_template = None

        # Do
        mock_value = Mock()
        result = Result(mock_value, TestResults.LABEL)
        results.show_results(result, results_title=TestResults.TITLE)

        # Check
        assert mock_process.cached_show_results == [result]
        assert mock_process.cached_show_results_title == TestResults.TITLE
        assert mock_Stage.results_template is None

    @patch('coolNewLanguage.src.stage.results.template_from_select_statement')
    @patch('sqlalchemy.select')
    def test_result_template_of_sql_alch_table_happy_path(
            self,
            mock_select: Mock,
            mock_template_from_select_statement: Mock
    ):
        # Setup
        # Mock table to pass in
        mock_table = Mock(spec=sqlalchemy.Table)
        # Mock sqlalchemy.select
        mock_stmt = Mock()
        mock_select.return_value = mock_stmt
        # Mock template_from_select_statement
        mock_template_from_select_statement.return_value = TestResults.RESULT_HTML

        # Do
        html_table = result_template_of_sql_alch_table(mock_table)

        # Check
        # Check select was called on table
        mock_select.assert_called_with(mock_table)
        # Check template_from_select_statement was called on mock_stmt
        mock_template_from_select_statement.assert_called_with(mock_stmt)
        # Check return value
        assert html_table == TestResults.RESULT_HTML

    def test_result_template_of_sql_alch_table_non_sql_alchemy_table_table(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected table to be a sqlalchemy Table"):
            result_template_of_sql_alch_table(Mock())

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_result_template_of_row_list_happy_path(self, mock_running_tool: Mock):
        # Setup
        # Mock rows
        row1, row2 = [Mock(spec=Row), Mock(spec=Row)]
        col_names = [TestResults.COL_NAME1, TestResults.COL_NAME2]
        row1.keys = Mock(return_value=col_names)
        row2.keys = Mock(return_value=col_names)
        # Mock indexing into each row
        row1_dict = {
            TestResults.COL_NAME1: Mock(get_val=Mock(return_value="Oski")),
            TestResults.COL_NAME2: Mock(get_val=Mock(return_value="Bear"))
        }
        row1.__getitem__ = lambda _, c: row1_dict[c]
        row2_dict = {
            TestResults.COL_NAME1: Mock(get_val=Mock(return_value="Carol")),
            TestResults.COL_NAME2: Mock(get_val=Mock(return_value="Christ"))
        }
        row2.__getitem__ = lambda _, c: row2_dict[c]
        # Mock jinja environment and template
        mock_running_tool.jinja_environment = Mock()
        mock_jinja_template = Mock(spec=jinja2.Template)
        mock_running_tool.jinja_environment.get_template = Mock(return_value=mock_jinja_template)
        mock_jinja_template.render = Mock(return_value=TestResults.RESULT_HTML)

        # Do
        result_html = results.result_template_of_row_list([row1, row2])

        # Check
        mock_running_tool.jinja_environment.get_template.assert_called_with(name=consts.TABLE_RESULT_TEMPLATE_FILENAME)
        mock_jinja_template.render.assert_called_with(
            col_names=col_names,
            rows=[
                {TestResults.COL_NAME1: "Oski", TestResults.COL_NAME2: "Bear"},
                {TestResults.COL_NAME1: "Carol", TestResults.COL_NAME2: "Christ"}
            ]
        )
        assert TestResults.RESULT_HTML == result_html

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_result_template_of_list_list_happy_path(self, mock_running_tool: Mock):
        # Setup
        # Construct rows to pass
        col_names = [TestResults.COL_NAME1, TestResults.COL_NAME2]
        rows = [col_names, ["Oski", "Bear"], ["Carol", "Christ"]]
        # Mock jinja environment and template
        mock_running_tool.jinja_environment = Mock()
        mock_jinja_template = Mock(spec=jinja2.Template)
        mock_running_tool.jinja_environment.get_template = Mock(return_value=mock_jinja_template)
        mock_jinja_template.render = Mock(return_value=TestResults.RESULT_HTML)

        # Do
        result_html = results.result_template_of_list_list(rows)

        # Check
        mock_running_tool.jinja_environment.get_template.assert_called_with(name=consts.TABLE_RESULT_TEMPLATE_FILENAME)
        mock_jinja_template.render.assert_called_with(
            col_names=col_names,
            rows=[
                {TestResults.COL_NAME1: "Oski", TestResults.COL_NAME2: "Bear"},
                {TestResults.COL_NAME1: "Carol", TestResults.COL_NAME2: "Christ"}
            ]
        )
        assert TestResults.RESULT_HTML == result_html

    def test_result_template_of_dataframe(self):
        # Setup
        # Mock dataframe
        mock_df = Mock(to_html=Mock(return_value=TestResults.RESULT_HTML))

        # Do
        result_html = results.result_template_of_dataframe(mock_df)

        # Check
        assert TestResults.RESULT_HTML == result_html
