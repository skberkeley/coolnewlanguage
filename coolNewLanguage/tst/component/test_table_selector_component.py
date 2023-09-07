from unittest.mock import Mock, patch, call

import pytest
import sqlalchemy

import coolNewLanguage.src.stage.config
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

    @patch.object(coolNewLanguage.src.component.input_component.InputComponent, '__init__')
    def test_table_selector_component_happy_path(self, mock_input_component_init: Mock):
        # Do
        table_selector_component = TableSelectorComponent(
            TestTableSelectorComponent.LABEL,
            TestTableSelectorComponent.COLUMNS
        )

        # Check
        # Check fields
        assert table_selector_component.label == TestTableSelectorComponent.LABEL
        assert table_selector_component.columns == TestTableSelectorComponent.COLUMNS
        assert table_selector_component.only_user_tables
        # Check that the columns were registered on the table selector
        TestTableSelectorComponent.COLUMN1.register_on_table_selector.assert_called_with(table_selector_component)
        TestTableSelectorComponent.COLUMN2.register_on_table_selector.assert_called_with(table_selector_component)
        # Check that InputComponent's __init__ was called
        mock_input_component_init.assert_called_with(expected_type=str)

    @patch.object(coolNewLanguage.src.component.input_component.InputComponent, '__init__')
    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_table_selector_component_config_building_template_happy_path(
            self,
            mock_tool_under_construction: Mock,
            mock_input_component_init: Mock
    ):
        # Setup
        config.building_template = True
        # Mock get_template
        mock_template = Mock()
        mock_get_template = Mock(return_value=mock_template)
        mock_tool_under_construction.jinja_environment = Mock(get_template=mock_get_template)

        # Do
        table_selector_component = TableSelectorComponent(
            TestTableSelectorComponent.LABEL,
            TestTableSelectorComponent.COLUMNS
        )

        # Check
        # Check fields
        assert table_selector_component.label == TestTableSelectorComponent.LABEL
        assert table_selector_component.columns == TestTableSelectorComponent.COLUMNS
        # Check that the columns were registered on the table selector
        TestTableSelectorComponent.COLUMN1.register_on_table_selector.assert_called_with(table_selector_component)
        TestTableSelectorComponent.COLUMN2.register_on_table_selector.assert_called_with(table_selector_component)
        # Check that InputComponent's __init__ was called
        mock_input_component_init.assert_called_with(expected_type=str)
        # Check that the template was accessed and set
        mock_get_template.assert_called_with(consts.TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME)
        assert table_selector_component.template == mock_template

    def new_input_component_init(self, expected_type: type):
        self.value = TestTableSelectorComponent.TABLE_NAME

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    @patch('sqlalchemy.Table')
    @patch('sqlalchemy.inspect')
    @patch('coolNewLanguage.src.stage.process.running_tool')
    def test_table_selector_component_process_handling_post_happy_path(
            self,
            mock_running_tool: Mock,
            mock_sqlalchemy_inspect: Mock,
            mock_sqlalchemy_table: Mock
    ):
        # Setup
        process.handling_post = True
        # Mock the running_tool's db_metadata_obj and db_engine
        mock_db_metadata_obj, mock_db_engine = Mock(), Mock()
        mock_running_tool.db_metadata_obj, mock_running_tool.db_engine = mock_db_metadata_obj, mock_db_engine
        # Mock sqlalchemy.inspect to return a mock Inspector object with a mock reflect_table method
        mock_inspector = Mock(reflect_table=Mock())
        mock_sqlalchemy_inspect.return_value = mock_inspector
        # Mock a sqlachemy table
        mock_sqlalchemy_table_instance = Mock()
        mock_sqlalchemy_table.return_value = mock_sqlalchemy_table_instance

        # Do
        table_selector_component = TableSelectorComponent(
            TestTableSelectorComponent.LABEL,
            TestTableSelectorComponent.COLUMNS
        )

        # Check
        # Check fields
        assert table_selector_component.label == TestTableSelectorComponent.LABEL
        assert table_selector_component.columns == TestTableSelectorComponent.COLUMNS
        # Check that the columns were registered on the table selector
        TestTableSelectorComponent.COLUMN1.register_on_table_selector.assert_called_with(table_selector_component)
        TestTableSelectorComponent.COLUMN2.register_on_table_selector.assert_called_with(table_selector_component)
        # Check self.value
        assert table_selector_component.value == mock_sqlalchemy_table_instance
        # Check that the sqlalchemy Table was instantiated correctly
        mock_sqlalchemy_table.assert_called_with(TestTableSelectorComponent.TABLE_NAME, mock_db_metadata_obj)
        # Check that sqlalchemy.inspect was called
        mock_sqlalchemy_inspect.assert_called_with(mock_db_engine)
        # Check that the inspector's reflect_table method was called
        mock_inspector.reflect_table.assert_called_with(table=mock_sqlalchemy_table_instance, include_columns=None)

    def test_table_selector_component_non_string_label(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            TableSelectorComponent(Mock())

    def test_table_selector_component_non_list_columns(self):
        with pytest.raises(TypeError, match="Expected columns to be a list"):
            TableSelectorComponent(TestTableSelectorComponent.LABEL, Mock())

    def test_table_selector_component_columns_has_non_column_selector_component(self):
        with pytest.raises(TypeError, match="Expected each element of columns to be a ColumnSelectorComponent"):
            TableSelectorComponent(TestTableSelectorComponent.LABEL, [TestTableSelectorComponent.COLUMN1, Mock()])

    @pytest.fixture
    @patch.object(coolNewLanguage.src.component.input_component.InputComponent, '__init__')
    def table_selector_component(self, _: Mock):
        return TableSelectorComponent(TestTableSelectorComponent.LABEL, TestTableSelectorComponent.COLUMNS, True)

    @patch('json.dumps')
    @patch('coolNewLanguage.src.component.table_selector_component.get_column_names_from_table_name')
    @patch('coolNewLanguage.src.component.table_selector_component.get_table_names_from_tool')
    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_table_selector_component_paint(
            self,
            mock_tool_under_construction: Mock,
            mock_get_table_names_from_tool: Mock,
            mock_get_column_names_from_table_name: Mock,
            mock_json_dumps: Mock,
            table_selector_component: TableSelectorComponent
    ):
        # Setup
        # Mock get_table_names_from_tool
        table1, table2 = "a table", "another table"
        mock_get_table_names_from_tool.return_value = [table1, table2]
        # Mock get_column_names_from_table_name
        col1, col2 = "a column", "wow another column"
        mock_get_column_names_from_table_name.return_value = [col1, col2]
        # Mock json.dumps
        json_value = "{totallyvalid:json}"
        mock_json_dumps.return_value = json_value
        # Mock table_selector_component's render
        rendered_template = "look ma i'm a table selector"
        table_selector_component.template = Mock(render=Mock(return_value=rendered_template))

        # Do
        painted_table_selector_component = table_selector_component.paint()

        # Check
        # Check get_table_names_from_tool was called correctly
        mock_get_table_names_from_tool.assert_called_with(mock_tool_under_construction, True)
        # Check get_column_names_from_table_name was called as expected
        mock_get_column_names_from_table_name.assert_has_calls(
            [call(mock_tool_under_construction, table1), call(mock_tool_under_construction, table2)]
        )
        # Check json.dumps was called as expected
        expected_table_column_map = {
            table1: [col1, col2],
            table2: [col1, col2]
        }
        mock_json_dumps.assert_called_with(expected_table_column_map)
        # Check template's render method was called and returned as expected
        table_selector_component.template.render.assert_called_with(
            component=table_selector_component,
            tables=[table1, table2],
            table_column_map_json=json_value,
            column_selectors=TestTableSelectorComponent.COLUMNS
        )
        assert painted_table_selector_component == rendered_template

    @patch('coolNewLanguage.src.component.table_selector_component.Row')
    @patch('coolNewLanguage.src.component.table_selector_component.get_rows_of_table')
    def test_table_selector_component_iter(
            self,
            mock_get_rows_of_table: Mock,
            mock_row: Mock,
            table_selector_component: TableSelectorComponent
    ):
        # Setup
        # Mock get_rows_of_table
        sqlalchemy_row1, sqlalchemy_row2 = Mock(spec=sqlalchemy.Row), Mock(spec=sqlalchemy.Row)
        sqlalchemy_rows = [sqlalchemy_row1, sqlalchemy_row2]
        mock_get_rows_of_table.return_value = sqlalchemy_rows
        # Mock Row
        mock_row_instance = Mock()
        mock_row.return_value = mock_row_instance
        # Mock table_selector_component's value as a table
        mock_table = Mock(sqlalchemy.Table)
        table_selector_component.value = mock_table

        # Do, Check
        for row in table_selector_component:
            assert row == mock_row_instance

        mock_row.assert_has_calls(
            [
                call(table=mock_table, sqlalchemy_row=sqlalchemy_row1),
                call(table=mock_table, sqlalchemy_row=sqlalchemy_row2)
            ]
        )