from unittest.mock import Mock, patch

import pytest
import sqlalchemy

from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME


class TestRow:
    ROW_ID = 1
    NAME_COLUMN = "Names"
    INVALID_COLUMN_NAME = "not a real column"
    OSKI = "Oski"
    OSKI_BEAR = "Oski Bear"
    ROW_DICT = {
        DB_INTERNAL_COLUMN_ID_NAME: ROW_ID,
        NAME_COLUMN: OSKI
    }

    def test_row_happy_path(self):
        # Setup
        sqlalchemy_table = Mock(spec=sqlalchemy.Table)
        sqlalchemy_row = Mock(spec=sqlalchemy.Row)
        sqlalchemy_row._asdict.return_value = TestRow.ROW_DICT

        # Do
        row = Row(table=sqlalchemy_table, sqlalchemy_row=sqlalchemy_row)

        # Check
        # Check row_mapping is set to sqlalchemy_row's _asdict
        assert row.row_mapping == TestRow.ROW_DICT
        # Check table set properly
        assert row.table == sqlalchemy_table
        # Check row_id set properly
        assert row.row_id == TestRow.ROW_ID
        # Check cell_mapping initialized properly
        assert row.cell_mapping == {}

    def test_row_non_sqlalchemy_table_table(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected table to be a sqlalchemy Table"):
            Row(Mock(), Mock(spec=sqlalchemy.Row))

    def test_row_non_sql_alchemy_row_row(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected sqlalchemy_row to be a sqlalchemy Row"):
            Row(Mock(spec=sqlalchemy.Table), Mock())

    @pytest.fixture
    def row(self):
        sqlalchemy_row = Mock(spec=sqlalchemy.Row)
        sqlalchemy_row._asdict.return_value = TestRow.ROW_DICT
        return Row(table=Mock(spec=sqlalchemy.Table), sqlalchemy_row=sqlalchemy_row)

    def test_getitem_item_is_string_cell_not_in_cell_mapping(self, row: Row):
        # Setup
        # Check cell not in row's cell_mapping
        assert TestRow.NAME_COLUMN not in row.cell_mapping

        # Do
        cell1 = row[TestRow.NAME_COLUMN]
        cell2 = row.__getitem__(TestRow.NAME_COLUMN)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check cell now in row's cell_mapping
        assert TestRow.NAME_COLUMN in row.cell_mapping
        # Check values of Cell
        expected_cell_val = Cell(
            table=row.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row.row_id,
            expected_type=None,
            val=TestRow.OSKI
        )
        assert cell1 == expected_cell_val

    def test_getitem_item_is_column_selector_component_cell_not_in_cell_mapping(self, row: Row):
        # Setup
        # Check cell not in row's cell_mapping
        assert TestRow.NAME_COLUMN not in row.cell_mapping
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_val_type = mock_type

        # Do
        cell1 = row[column_selector_component]
        cell2 = row.__getitem__(column_selector_component)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check cell now in row's cell_mapping
        assert TestRow.NAME_COLUMN in row.cell_mapping
        # Check values of Cell
        expected_cell_val = Cell(
            table=row.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row.row_id,
            expected_type=mock_type,
            val=TestRow.OSKI
        )
        assert cell1 == expected_cell_val

    def test_getitem_item_is_string_cell_already_in_cell_mapping(self, row: Row):
        # Setup
        mock_cell = Mock(spec=Cell)
        row.cell_mapping[TestRow.NAME_COLUMN] = mock_cell

        # Do
        cell1 = row[TestRow.NAME_COLUMN]
        cell2 = row.__getitem__(TestRow.NAME_COLUMN)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check values of Cell
        assert cell1 == mock_cell

    def test_getitem_item_is_not_string_or_column_selector_component(self, row: Row):
        # Do, Check
        with pytest.raises(TypeError, match="Expected item to be a string or ColumnSelectorComponent"):
            _ = row[Mock()]

    @patch('coolNewLanguage.src.row.Cell')
    def test_setitem_key_is_string_happy_path(self, mock_cell: Mock, row: Row):
        # Setup
        # Check that key is not in cell_mapping
        assert TestRow.NAME_COLUMN not in row.cell_mapping
        # Mock the cell instance that is created for row's cell_mapping
        mock_cell_instance = Mock(spec=Cell)
        mock_cell.return_value = mock_cell_instance
        # Mock cell.set so we can verify the call later
        mock_cell_set = Mock()
        mock_cell_instance.set = mock_cell_set

        # Do
        row[TestRow.NAME_COLUMN] = TestRow.OSKI_BEAR

        # Check
        # Check that key is now set in cell_mapping
        assert TestRow.NAME_COLUMN in row.cell_mapping
        # Check Cell was instantiated with appropriate arguments
        mock_cell.assert_called_with(
            table=row.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row.row_id,
            expected_type=None,
            val=row.row_mapping[TestRow.NAME_COLUMN]
        )
        # Check that cell.set was called
        mock_cell_set.assert_called_with(TestRow.OSKI_BEAR)

    @patch('coolNewLanguage.src.row.Cell')
    def test_setitem_key_is_column_selector_component_happy_path(self, mock_cell: Mock, row: Row):
        # Setup
        # Create mock column selector to use
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_type = mock_type
        # Check that key is not in cell_mapping
        assert TestRow.NAME_COLUMN not in row.cell_mapping
        # Mock the cell instance that is created for row's cell_mapping
        mock_cell_instance = Mock(spec=Cell)
        mock_cell.return_value = mock_cell_instance
        mock_cell_instance.expected_type = Mock(spec=type)
        # Mock cell.set so we can verify the call later
        mock_cell_set = Mock()
        mock_cell_instance.set = mock_cell_set

        # Do
        row[column_selector_component] = TestRow.OSKI_BEAR

        # Check
        # Check that key is now set in cell_mapping
        assert TestRow.NAME_COLUMN in row.cell_mapping
        # Check Cell was instantiated with appropriate arguments
        mock_cell.assert_called_with(
            table=row.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row.row_id,
            expected_type=mock_type,
            val=row.row_mapping[TestRow.NAME_COLUMN]
        )
        # Check that cell.set was called
        mock_cell_set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_string_key_in_cell_mapping_happy_path(self, row: Row):
        # Setup
        # Put a mock cell in row's cell_mapping
        mock_cell = Mock(spec=Cell)
        row.cell_mapping[TestRow.NAME_COLUMN] = mock_cell

        # Do
        row[TestRow.NAME_COLUMN] = TestRow.OSKI_BEAR

        # Check
        # Check that the mock cell's set method was called
        mock_cell.set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_column_selector_component_key_in_cell_mapping_happy_path(self, row: Row):
        # Setup
        # Put a mock cell in row's cell_mapping
        mock_cell = Mock(spec=Cell)
        # Set mock_cell's type to None to check if it's updated later
        mock_cell.expected_type = None
        row.cell_mapping[TestRow.NAME_COLUMN] = mock_cell
        # Create mock column selector to use
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_type = mock_type

        # Do
        row[column_selector_component] = TestRow.OSKI_BEAR

        # Check
        # Check that the mock cell's expected type was updated
        assert mock_cell.expected_type == mock_type
        # Check that the mock cell's set method was called
        mock_cell.set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_string_key_is_not_valid_column_name(self, row: Row):
        # Do, Check
        with pytest.raises(ValueError, match=f"Key {TestRow.INVALID_COLUMN_NAME} is not a valid column name"):
            row[TestRow.INVALID_COLUMN_NAME] = TestRow.OSKI

    def test_setitem_key_is_column_selector_component_key_is_not_valid_column_name(self, row: Row):
        # Setup
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.INVALID_COLUMN_NAME
        column_selector_component.expected_type = None

        # Do, Check
        with pytest.raises(ValueError, match=f"Key {TestRow.INVALID_COLUMN_NAME} is not a valid column name"):
            row[column_selector_component] = TestRow.OSKI

    def test_setitem_key_is_not_string_or_column_selector_component(self, row: Row):
        # Do, Check
        with pytest.raises(TypeError, match="Expected key to be a string or a ColumnSelectorComponent"):
            row[Mock()] = Mock()

    def test_keys_happy_path(self, row: Row):
        # Do, Check
        assert row.keys() == TestRow.ROW_DICT.keys()

    def test_contains_happy_path(self, row: Row):
        # Do, Check
        assert TestRow.NAME_COLUMN in row
        assert TestRow.INVALID_COLUMN_NAME not in row

    def test_iter_happy_path(self, row: Row):
        # Do, Check
        vals = []
        for val in row:
            vals.append(val)
        assert vals == [TestRow.ROW_ID, TestRow.OSKI]