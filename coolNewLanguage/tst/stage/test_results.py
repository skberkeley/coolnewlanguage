from unittest.mock import patch, Mock, MagicMock

import jinja2
import pytest
import sqlalchemy

import coolNewLanguage.src.stage.results
from coolNewLanguage.src import consts
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process, results
from coolNewLanguage.src.stage.results import show_results, result_template_of_sql_alch_table, Result, add_result
from coolNewLanguage.src.stage.stage import Stage


class TestResults:
    LABEL = "Drink me"
    TITLE = "BIG OL' TABLE"
    RESULT_HTML = "<totally_html>"

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        process.handling_post = False
        results.results = []

        yield

        process.handling_post = True
        results.results = []

    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_show_results__happy_path(
            self,
            mock_running_tool: Mock
    ):
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
        # Put some stuff in results
        mock_result = Mock(spec=Result)
        results.results = [mock_result]

        # Do
        show_results(results_title=TestResults.TITLE)

        # Check
        # Check that the jinja template was loaded from the right file
        mock_get_template.assert_called_with(name=consts.STAGE_RESULTS_TEMPLATE_FILENAME)
        # Check that the template's render was called as expected
        mock_template.render.assert_called_with(
            results_title=TestResults.TITLE,
            results=[mock_result]
        )
        # Check that the rendered template was set on Stage
        assert Stage.results_template == mock_rendered_template
        # Check that results was reset
        assert results.results == []
        # Reset process.handling_post as part of cleanup
        process.handling_post = False

    def test_show_results_non_string_results_title(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected results_title to be a string"):
            show_results(results_title=Mock())

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
        show_results(results_title=TestResults.TITLE)

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
        # Put some stuff in results
        mock_result = Mock(spec=Result)
        results.results = [mock_result]

        # Do
        show_results()

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
        # Check that results was reset
        assert results.results == []
        # Reset process.handling_post as part of cleanup
        process.handling_post = False

    @patch('coolNewLanguage.src.stage.results.result_template_of_value')
    def test_add_result_happy_path(self, mock_result_template_of_value: Mock):
        # Setup
        process.handling_post = True
        mock_value = Mock()
        # Mock the html value being returned
        mock_result_template_of_value.return_value = TestResults.RESULT_HTML

        # Do
        add_result(mock_value)

        # Check
        # Check that result_template_of_value was called
        mock_result_template_of_value.assert_called_with(mock_value)
        # Check that results was appended to
        assert results.results == [Result(TestResults.RESULT_HTML)]

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
