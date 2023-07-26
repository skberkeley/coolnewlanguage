from unittest.mock import Mock, patch

import pytest
import sqlalchemy

import coolNewLanguage.src.component.input_component
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent


class TestColumnSelectorComponent:
    LABEL = "click a gd column"
    EXPECTED_VAL_TYPE = Mock(spec=type)
    COLUMN_NAME = "a gd column"

    def new_input_component_init(self, expected_type: type):
        self.value = TestColumnSelectorComponent.COLUMN_NAME

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    def test_column_selector_component_happy_path(self):
        # Do
        column_selector_component = ColumnSelectorComponent(
            TestColumnSelectorComponent.LABEL,
            TestColumnSelectorComponent.EXPECTED_VAL_TYPE
        )

        # Check
        # Check fields
        assert column_selector_component.table_selector is None
        assert column_selector_component.label == TestColumnSelectorComponent.LABEL
        assert column_selector_component.expected_val_type == TestColumnSelectorComponent.EXPECTED_VAL_TYPE
        assert column_selector_component.emulated_column == TestColumnSelectorComponent.COLUMN_NAME

    def test_column_selector_component_non_string_label(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            ColumnSelectorComponent(Mock())

    def test_column_selector_component_non_type_expected_val_type(self):
        with pytest.raises(TypeError, match="Expected expected_val_type to be a type"):
            ColumnSelectorComponent(TestColumnSelectorComponent.LABEL, Mock())

    @pytest.fixture
    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    def column_selector_component(self):
        return ColumnSelectorComponent(TestColumnSelectorComponent.LABEL, TestColumnSelectorComponent.EXPECTED_VAL_TYPE)

    def test_register_on_table_selector(self, column_selector_component: ColumnSelectorComponent):
        # Setup
        # Mock a TableSelectorComponent
        mock_table_selector_component = Mock(spec=TableSelectorComponent)

        # Do
        column_selector_component.register_on_table_selector(mock_table_selector_component)

        # Check
        assert column_selector_component.table_selector == mock_table_selector_component

    def test_register_on_table_selector_non_table_selector_component_table_selector(
            self,
            column_selector_component: ColumnSelectorComponent
    ):
        with pytest.raises(TypeError, match="Expected table_selector to be a TableSelectorComponent"):
            column_selector_component.register_on_table_selector(Mock())

    def test_register_on_table_selector_already_registered_on_a_table_selector(
            self,
            column_selector_component: ColumnSelectorComponent
    ):
        # Setup
        column_selector_component.table_selector = Mock()

        # Do, Check
        with pytest.raises(
                ValueError,
                match="This ColumnSelectorComponent is already registered on a TableSelectorComponent"
        ):
            column_selector_component.register_on_table_selector(Mock(spec=TableSelectorComponent))

    @patch('coolNewLanguage.src.component.column_selector_component.Cell')
    @patch('coolNewLanguage.src.component.column_selector_component.iterate_over_column')
    def test_iter_happy_path(
            self,
            mock_iterate_over_column: Mock,
            mock_cell: Mock,
            column_selector_component: ColumnSelectorComponent
    ):
        # Setup
        # Mock column_selector_component's table_selector's value to be a sqlalchemy Table
        mock_sqlalchemy_table = Mock(spec=sqlalchemy.Table)
        column_selector_component.table_selector = Mock(value=mock_sqlalchemy_table)
        # Mock iterate_over_columns
        row_id_val_pairs = [("a row", "its value"), ("no way another row", "wow, its value!")]
        mock_iterate_over_column.return_value = iter(row_id_val_pairs)
        # Mock Cell
        mock_cell_instance = Mock()
        mock_cell.return_value = mock_cell_instance

        # Do, Check
        for cell, row_id_val_pair in zip(column_selector_component, row_id_val_pairs):
            # Check that cell is mock cell instance
            assert cell == mock_cell_instance
            # Check call to Cell
            row_id, val = row_id_val_pair
            mock_cell.assert_called_with(
                mock_sqlalchemy_table,
                TestColumnSelectorComponent.COLUMN_NAME,
                row_id, TestColumnSelectorComponent.EXPECTED_VAL_TYPE,
                val
            )
