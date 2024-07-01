from unittest.mock import patch, Mock, MagicMock

import jinja2
import pytest
import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process, results
from coolNewLanguage.src.stage.results import show_results, result_template_of_sql_alch_table, Result
from coolNewLanguage.src.stage.stage import Stage


class TestResults:
    LABEL = "Drink me"
    TITLE = "BIG OL' TABLE"
    RESULT_HTML = "<totally_html>"
    COL_NAME1 = "First Name"
    COL_NAME2 = "Last Name"

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        process.handling_post = False

        yield

        process.handling_post = True

    @patch('coolNewLanguage.src.stage.results.result_template_of_value')
    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results_result_object_happy_path(
            self,
            mock_running_tool: Mock,
            mock_result_template_of_value: Mock
    ):
        # Setup
        # Set process.handling_post to True so show_results doesn't return early
        process.handling_post = True
        # Mock result_template_of_value function
        mock_result_template_of_value.return_value = TestResults.RESULT_HTML
        # Create a mock Jinja template
        mock_template = Mock(jinja2.Template)
        mock_rendered_template = Mock(spec=str)
        mock_template.render = Mock(return_value=mock_rendered_template)
        # Mock the Jinja get_template method
        mock_running_tool.jinja_environment = Mock()
        mock_get_template = Mock(return_value=mock_template)
        mock_running_tool.jinja_environment.get_template = mock_get_template
        # Mock some results
        mock_value = Mock()
        mock_result = Mock(spec=Result, value=mock_value)

        # Do
        show_results(mock_result, results_title=TestResults.TITLE)

        # Check
        # Check that the passed Result object had its html_value set
        assert mock_result.html_value == TestResults.RESULT_HTML
        # Check that the jinja template was loaded from the right file
        mock_get_template.assert_called_with(name=consts.STAGE_RESULTS_TEMPLATE_FILENAME)
        # Check that the template's render was called as expected
        mock_template.render.assert_called_with(
            results_title=TestResults.TITLE,
            results=[mock_result]
        )
        # Check that the rendered template was set on Stage
        assert Stage.results_template == mock_rendered_template
        # Reset process.handling_post as part of cleanup
        process.handling_post = False

    def test_show_results_non_string_results_title(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected results_title to be a string"):
            show_results([], results_title=Mock())

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results_not_handling_post(
            self,
            mock_running_tool: Mock
    ):
        # Setup
        # Mock the Jinja get_template method
        mock_running_tool.jinja_environment = Mock()
        mock_running_tool.jinja_environment.get_template = Mock()

        # Do
        show_results([], results_title=TestResults.TITLE)

        # Check
        # Check that get_template wasn't called
        mock_running_tool.jinja_environment.get_template.assert_not_called()

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results_empty_results_title(self, mock_running_tool: Mock):
        # Setup
        # Set process.handling_post to True so show_results doesn't return early
        process.handling_post = True
        # Create a mock Jinja template
        mock_template = Mock(jinja2.Template)
        mock_rendered_template = Mock(spec=str)
        mock_template.render = Mock(return_value=mock_rendered_template)
        # Mock the Jinja get_template method
        mock_running_tool.jinja_environment = Mock()
        mock_get_template = Mock(return_value=mock_template)
        mock_running_tool.jinja_environment.get_template = mock_get_template
        # Mock some results
        mock_result = Mock(spec=Result)
        mock_results = [mock_result]

        # Do
        show_results(mock_results)

        # Check
        # Check that the jinja template was loaded from the right file
        mock_get_template.assert_called_with(name=consts.STAGE_RESULTS_TEMPLATE_FILENAME)
        # Check that the template's render was called as expected
        mock_template.render.assert_called_with(
            results_title="Results",
            results=[mock_result]
        )
        # Check that the rendered template was set on Stage
        assert Stage.results_template == mock_rendered_template
        # Reset process.handling_post as part of cleanup
        process.handling_post = False

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
