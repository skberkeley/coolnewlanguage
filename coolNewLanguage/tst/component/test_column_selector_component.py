from unittest.mock import Mock, patch, MagicMock

import pytest

import coolNewLanguage.src.component.input_component
from coolNewLanguage.src import consts
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.stage import process


class TestColumnSelectorComponent:
    LABEL = "click a gd column"
    EXPECTED_VAL_TYPE = Mock(spec=type)
    COLUMN_NAME = "a gd column"
    TABLE_NAME = "Arthur's round one"

    @patch('coolNewLanguage.src.component.column_selector_component.process')
    def test_column_selector_component_happy_path(self, mock_process: Mock):
        # Setup
        process.handling_post = True
        process.post_body = Mock(
            getall=Mock(return_value=[TestColumnSelectorComponent.TABLE_NAME, TestColumnSelectorComponent.COLUMN_NAME])
        )
        # Mock running_tool's tables
        mock_filtered_dataframe = MagicMock()
        mock_dataframe = MagicMock(__getitem__=Mock(return_value=mock_filtered_dataframe))
        mock_process.running_tool.tables = MagicMock(__getitem__=Mock(return_value=mock_dataframe))

        # Do
        column_selector_component = ColumnSelectorComponent(TestColumnSelectorComponent.LABEL)

        # Check
        # Check fields
        assert column_selector_component.label == TestColumnSelectorComponent.LABEL
        assert column_selector_component.num_columns == 1
        assert column_selector_component.table_name == TestColumnSelectorComponent.TABLE_NAME
        assert column_selector_component.value == mock_filtered_dataframe

        process.handling_post = False


    def test_column_selector_component_non_string_label(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            ColumnSelectorComponent(Mock())

    def test_column_selector_component_non_int_num_columns(self):
        with pytest.raises(TypeError, match="Expected num_columns to be an int"):
            ColumnSelectorComponent(num_columns=Mock())

    @pytest.fixture
    def column_selector_component(self):
        return ColumnSelectorComponent(TestColumnSelectorComponent.LABEL)

    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_paint_happy_path(
            self,
            mock_tool_under_construction: Mock,
            column_selector_component: ColumnSelectorComponent
    ):
        # Setup
        # Mock the template
        mock_template = Mock()
        mock_tool_under_construction.jinja_environment.get_template.return_value = mock_template
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
        rendered_component = column_selector_component.paint()

        # Check
        mock_tool_under_construction.jinja_environment.get_template.assert_called_once_with(
            name=consts.COLUMN_SELECTOR_COMPONENT_TEMPLATE_FILENAME
        )
        # Check that the rendered template was returned
        assert rendered_component == mock_rendered_template
        # Check that the template was rendered with the expected arguments
        mock_template.render.assert_called_once_with(
            label=TestColumnSelectorComponent.LABEL,
            tables=[{'name': 'table1', 'cols': ['col1', 'col2'], 'rows': mock_rows, 'transient_id': 0}],
            num_preview_cols=ColumnSelectorComponent.NUM_PREVIEW_COLS,
            component_id=column_selector_component.component_id,
            context=consts.GET_TABLE_COLUMN_SELECT
        )
