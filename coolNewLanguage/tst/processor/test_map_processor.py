from unittest.mock import Mock, NonCallableMock, patch

import pytest
import sqlalchemy

import coolNewLanguage.src.processor.map_processor
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.processor.map_processor import MapProcessor
from coolNewLanguage.src.stage import process


class TestMapProcessor:
    MOCK_CELLS = [
        Mock(spec=Cell, row_id=0),
        Mock(spec=Cell, row_id=1)
    ]
    FUNC_RETURN_VALUE = "MY BOI OSKI"
    MOCK_TABLE = Mock(sqlalchemy.Table)
    COL_NAME = "Best College Mascots"

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.processor.map_processor.update_column')
    def test_map_processor_handling_post_happy_path(self, mock_update_column: Mock, mock_running_tool: Mock):
        # Setup
        process.handling_post = True
        # Mock col, cells
        mock_col = Mock(
            spec=ColumnSelectorComponent,
            table_selector=Mock(value=TestMapProcessor.MOCK_TABLE),
            emulated_column=TestMapProcessor.COL_NAME
        )
        mock_col.__iter__ = Mock(return_value=iter(TestMapProcessor.MOCK_CELLS))
        # Mock func
        mock_func = Mock()
        mock_func.return_value = TestMapProcessor.FUNC_RETURN_VALUE

        # Do
        map_processor = MapProcessor(mock_col, mock_func)

        # Check
        # Check update_column was called as expected
        expected_row_id_and_vals = [(c.row_id, TestMapProcessor.FUNC_RETURN_VALUE) for c in TestMapProcessor.MOCK_CELLS]
        mock_update_column.assert_called_with(
            tool=mock_running_tool,
            table=TestMapProcessor.MOCK_TABLE,
            col_name=TestMapProcessor.COL_NAME,
            row_id_val_pairs=expected_row_id_and_vals
        )
        assert map_processor.result == mock_col

        # Cleanup
        process.handling_post = False

    @patch('coolNewLanguage.src.processor.map_processor.update_column')
    def test_map_processor_not_handling_post_happy_path(self, mock_update_column: Mock):
        # Setup
        process.handling_post = False
        mock_col = Mock(
            spec=ColumnSelectorComponent,
            table_selector=Mock(value=TestMapProcessor.MOCK_TABLE),
            emulated_column=TestMapProcessor.COL_NAME
        )
        mock_func = Mock()

        # Do
        MapProcessor(mock_col, mock_func)

        # Check
        mock_func.assert_not_called()
        mock_update_column.assert_not_called()

    def test_map_processor_non_column_selector_component_col(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected col to be a ColumnSelectorComponent"):
            MapProcessor(Mock(), Mock())

    def test_map_processor_non_callable_func(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected func to be callable"):
            MapProcessor(Mock(spec=ColumnSelectorComponent), NonCallableMock())
