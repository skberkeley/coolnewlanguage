from unittest.mock import patch, Mock, MagicMock

import jinja2
import pytest
import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.results import show_results, result_template_of_sql_alch_table
from coolNewLanguage.src.stage.stage import Stage

RESULT_HTML = "some html"


def show_results_test_setup_helper(mock_result_template_func: Mock, mock_running_tool: Mock):
    # Set process.handling_post to True so show_results doesn't return early
    process.handling_post = True
    mock_result_template_func.return_value = RESULT_HTML
    # Create a mock Jinja template
    mock_template = Mock(jinja2.Template)
    mock_rendered_template = Mock(spec=str)
    mock_template.render = Mock(return_value=mock_rendered_template)
    # Mock the Jinja get_template method
    mock_running_tool.jinja_environment = Mock()
    mock_get_template = Mock(return_value=mock_template)
    mock_running_tool.jinja_environment.get_template = mock_get_template

    return mock_get_template, mock_template, RESULT_HTML, mock_rendered_template


def show_results_test_verify_helper(
        mock_get_template: Mock,
        mock_template: Mock,
        result_html: str,
        mock_rendered_template: Mock):
    # Check that the jinja template was loaded from the right file
    mock_get_template.assert_called_with(name=consts.STAGE_RESULTS_TEMPLATE_FILENAME)
    # Check that the template's render was called as expected
    mock_template.render.assert_called_with(
        results_title=TestResults.TITLE,
        label=TestResults.LABEL,
        result=result_html
    )
    # Check that the rendered template was set on Stage
    assert Stage.results_template == mock_rendered_template
    # Reset process.handling_post as part of cleanup
    process.handling_post = False


class TestResults:
    LABEL = "Drink me"
    TITLE = "BIG OL' TABLE"

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_sql_alch_table')
    def test_show_results_sqlalchemy_table_result_happy_path(
            self,
            mock_result_template_of_sql_alch_table: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result_template_of_sql_alch_table,
            mock_running_tool
        )
        # Mock result to test
        mock_result = Mock(spec=sqlalchemy.Table)

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that table was converted to html
        mock_result_template_of_sql_alch_table.assert_called_with(mock_result)
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_column_list')
    def test_show_results_column_list_result_happy_path(
            self,
            mock_result_template_of_column_list: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result_template_of_column_list,
            mock_running_tool
        )
        # Mock result to test
        mock_result = [Mock(spec=ColumnSelectorComponent), Mock(spec=ColumnSelectorComponent)]

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that columns were converted to html
        mock_result_template_of_column_list.assert_called_with(mock_result)
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_cell_list')
    def test_show_results_cell_list_result_happy_path(
            self,
            mock_result_template_of_cell_list: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result_template_of_cell_list,
            mock_running_tool
        )
        # Mock result to test
        mock_result = [Mock(spec=Cell), Mock(spec=Cell)]

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that cells were converted to html
        mock_result_template_of_cell_list.assert_called_with(mock_result)
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_row_list')
    def test_show_results_row_list_result_happy_path(
            self,
            mock_result_template_of_row_list: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result_template_of_row_list,
            mock_running_tool
        )
        # Mock result to test
        mock_result = [Mock(spec=Row), Mock(spec=Row)]

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that rows were converted to html
        mock_result_template_of_row_list.assert_called_with(mock_result)
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results_string_result_happy_path(self, mock_running_tool: Mock):
        # Setup
        # Mock result to test
        mock_result = MagicMock()
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result.__str__,
            mock_running_tool
        )

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that result was converted to string
        mock_result.__str__.assert_called()
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    def test_show_results_non_string_label(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected label to be a string"):
            show_results(result=Mock(), label=Mock(), results_title=TestResults.TITLE)

    def test_show_results_non_string_results_title(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected results_title to be a string"):
            show_results(result=Mock(), label=TestResults.LABEL, results_title=Mock())

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_sql_alch_table')
    def test_show_results_not_handling_post(
            self,
            mock_result_template_of_sql_alch_table: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Mock the result to pass in
        mock_result = Mock(spec=sqlalchemy.Table)
        # Mock the Jinja get_template method
        mock_running_tool.jinja_environment = Mock()
        mock_running_tool.jinja_environment.get_template = Mock()

        # Do
        show_results(result=mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Verify that we didn't try to cast mock_result to an HTML table
        mock_result_template_of_sql_alch_table.assert_not_called()
        # Check that get_template wasn't called
        mock_running_tool.jinja_environment.get_template.assert_not_called()

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.stage.results.result_template_of_sql_alch_table')
    def test_show_results_input_component_result(
            self,
            mock_result_template_of_sql_alch_table: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result_template_of_sql_alch_table,
            mock_running_tool
        )
        # Mock result to test
        mock_result = Mock(spec=InputComponent)
        mock_result.value = Mock(spec=sqlalchemy.Table)

        # Do
        show_results(mock_result, label=TestResults.LABEL, results_title=TestResults.TITLE)

        # Check
        # Check that table was converted to html
        mock_result_template_of_sql_alch_table.assert_called_with(mock_result.value)
        # Call verify helper
        show_results_test_verify_helper(mock_get_template, mock_template, mock_result_html, mock_rendered_template)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results_empty_results_title(self, mock_running_tool: Mock):
        # Setup
        # Mock result to test
        mock_result = MagicMock()
        # Call setup helper
        mock_get_template, mock_template, mock_result_html, mock_rendered_template = show_results_test_setup_helper(
            mock_result.__str__,
            mock_running_tool
        )

        # Do
        show_results(mock_result, label=TestResults.LABEL)

        # Check
        mock_template.render.assert_called_with(
            results_title="Results",
            label=TestResults.LABEL,
            result=mock_result_html
        )

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
        mock_template_from_select_statement.return_value = RESULT_HTML

        # Do
        html_table = result_template_of_sql_alch_table(mock_table)

        # Check
        # Check select was called on table
        mock_select.assert_called_with(mock_table)
        # Check template_from_select_statement was called on mock_stmt
        mock_template_from_select_statement.assert_called_with(mock_stmt)
        # Check return value
        assert html_table == RESULT_HTML

    def test_result_template_of_sql_alch_table_non_sql_alchemy_table_table(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected table to be a sqlalchemy Table"):
            result_template_of_sql_alch_table(Mock())
