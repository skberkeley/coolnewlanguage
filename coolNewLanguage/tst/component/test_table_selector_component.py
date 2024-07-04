from unittest.mock import Mock, patch, MagicMock

import pytest

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.stage import config, process


class TestTableSelectorComponent:
    LABEL = "pick a table"
    COLUMN1 = Mock(ColumnSelectorComponent, register_on_table_selector=Mock())
    COLUMN2 = Mock(ColumnSelectorComponent, register_on_table_selector=Mock())
    COLUMNS = [COLUMN1, COLUMN2]
    TABLE_NAME = "Arthur's round one"

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        config.building_template = False
        process.handling_post = False

        yield

        config.building_template = False
        process.handling_post = False

    @patch('coolNewLanguage.src.component.table_selector_component.process')
    def test_table_selector_component_happy_path(self, mock_process: Mock):
        # Setup
        process.handling_post = True
        process.post_body = Mock(getall=Mock(return_value=[TestTableSelectorComponent.TABLE_NAME]))
        # Mock running_tool's tables
        mock_dataframe = Mock()
        mock_process.running_tool.tables = MagicMock(__getitem__=Mock(return_value=mock_dataframe))

        # Do
        table_selector_component = TableSelectorComponent(TestTableSelectorComponent.LABEL)

        # Check
        # Check fields
        assert table_selector_component.label == TestTableSelectorComponent.LABEL
        assert table_selector_component.only_user_tables
        # Check that the value was set to the dataframe of the table
        assert table_selector_component.value == mock_dataframe

    def test_table_selector_component_non_string_label(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            TableSelectorComponent(Mock())

    def test_table_selector_component_non_bool_only_user_tables(self):
        with pytest.raises(TypeError, match="Expected only_user_tables to be a boolean"):
            TableSelectorComponent(TestTableSelectorComponent.LABEL, Mock())

    @pytest.fixture
    def table_selector_component(self):
        return TableSelectorComponent(TestTableSelectorComponent.LABEL)

    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_table_selector_component_paint(
            self,
            mock_tool_under_construction: Mock,
            table_selector_component: TableSelectorComponent
    ):
        # Setup
        # Mock get_template
        mock_template = Mock()
        mock_tool_under_construction.jinja_environment.get_template.return_value=mock_template
        # Mock get_table_names
        mock_tables = MagicMock()
        mock_tool_under_construction.tables = mock_tables
        mock_tables.get_table_names.return_value = ['table1']
        # Mock get_column_of_table
        mock_tables.get_columns_of_table.return_value = ['col1', 'col2']
        # Mock tables.__getitem__
        mock_rows = Mock()
        mock_tables.__getitem__.return_value = Mock(head=Mock(return_value=mock_rows))
        # Mock template.render
        mock_rendered_template = Mock()
        mock_template.render.return_value = mock_rendered_template

        # Do
        painted_table_selector_component = table_selector_component.paint()

        # Check
        # Check that the template was loaded
        mock_tool_under_construction.jinja_environment.get_template.assert_called_once_with(
            name=consts.TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME
        )
        # Check that the rendered template was returned
        assert painted_table_selector_component == mock_rendered_template
        # Check that the template was rendered with the expected arguments
        mock_template.render.assert_called_once_with(
            label=TestTableSelectorComponent.LABEL,
            tables=[{'name': 'table1', 'cols': ['col1', 'col2'], 'rows': mock_rows, 'transient_id': 0}],
            num_preview_cols=TableSelectorComponent.NUM_PREVIEW_COLS,
            component_id=table_selector_component.component_id,
            context=consts.GET_TABLE_TABLE_SELECT
        )
