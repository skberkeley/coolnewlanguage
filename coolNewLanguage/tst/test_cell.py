from unittest.mock import Mock, patch

import pytest
import sqlalchemy

from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.exceptions.CNLError import CNLError
from coolNewLanguage.tst.cell_test_utils import verify_cell


class TestCell:
    COL_NAME = "World 9 Ball Champions"
    ROW_ID = 1
    ANOTHER_ROW_ID = 2
    VAL = "Fransisco Sanchez Ruiz"
    YEAR_COL_NAME = "Year"
    YEAR_VAL = 2022
    OTHER_INT_VAL = 5
    OTHER_STR_VAL = " very wow!"

    @pytest.fixture
    def sqlalchemy_table(self) -> Mock:
        return Mock(spec=sqlalchemy.Table)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cell.get_cell_value')
    def test_cell_happy_path(self, mock_get_cell_value: Mock, mock_running_tool: Mock, sqlalchemy_table: Mock):
        # Do
        cell = Cell(table=sqlalchemy_table, col_name=TestCell.COL_NAME, row_id=TestCell.ROW_ID)

        # Check
        verify_cell(cell, table=sqlalchemy_table, col_name=TestCell.COL_NAME, row_id=TestCell.ROW_ID)
        assert cell.expected_type is None
        # Check that get_cell_value is called since val was not passed
        mock_get_cell_value.assert_called_with(mock_running_tool, sqlalchemy_table, TestCell.COL_NAME, TestCell.ROW_ID)

    @patch('coolNewLanguage.src.cell.get_cell_value')
    def test_cell_val_is_not_none_happy_path(self, mock_get_cell_value: Mock, sqlalchemy_table: Mock):
        # Do
        cell = Cell(table=sqlalchemy_table, col_name=TestCell.COL_NAME, row_id=TestCell.ROW_ID, val=TestCell.VAL)

        # Check
        verify_cell(cell, table=sqlalchemy_table, col_name=TestCell.COL_NAME, row_id=TestCell.ROW_ID, val=TestCell.VAL)
        assert cell.expected_type is None
        # Check that get_cell_value wasn't called, since we passed val
        mock_get_cell_value.assert_not_called()

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cell.get_cell_value')
    def test_cell_expected_type_is_not_none_happy_path(self,
                                                       mock_get_cell_value: Mock,
                                                       mock_running_tool: Mock,
                                                       sqlalchemy_table: Mock):
        # Setup
        mock_type = Mock(spec=type)
        mock_get_cell_value.return_value = TestCell.VAL

        # Do
        cell = Cell(table=sqlalchemy_table, col_name=TestCell.COL_NAME, row_id=TestCell.ROW_ID, expected_type=mock_type)

        # Check
        verify_cell(
            cell,
            table=sqlalchemy_table,
            col_name=TestCell.COL_NAME,
            row_id=TestCell.ROW_ID,
            expected_type=mock_type
        )
        # Check that the val was cast
        mock_type.assert_called_with(TestCell.VAL)

    def test_cell_table_is_not_sqlalchemy_table(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected table to be a sqlalchemy Table"):
            Cell(Mock(), TestCell.COL_NAME, TestCell.ROW_ID)

    def test_cell_col_name_is_not_string(self, sqlalchemy_table: Mock):
        # Do, Check
        with pytest.raises(TypeError, match="Expected col_name to be a string"):
            Cell(sqlalchemy_table, Mock(), TestCell.ROW_ID)

    def test_cell_row_id_is_not_int(self, sqlalchemy_table: Mock):
        # Do, Check
        with pytest.raises(TypeError, match="Expected row_id to be an int"):
            Cell(sqlalchemy_table, TestCell.COL_NAME, Mock())

    def test_cell_expected_type_is_not_a_type(self, sqlalchemy_table: Mock):
        # Do, Check
        with pytest.raises(TypeError, match="Expected expected_type to be a type"):
            Cell(sqlalchemy_table, TestCell.COL_NAME, TestCell.ROW_ID, expected_type=Mock())

    def test_cell_type_cast_fails(self, sqlalchemy_table):
        # Setup
        mock_type = Mock(spec=type, side_effect=ValueError)
        mock_type.__str__ = Mock(return_value="not a real type")

        # Do, Check
        with pytest.raises(CNLError, match=f"An error occurred while trying to cast {TestCell.VAL} to {mock_type}"):
            Cell(sqlalchemy_table, TestCell.COL_NAME, TestCell.ROW_ID, expected_type=mock_type, val=TestCell.VAL)

    @pytest.fixture
    def str_val_cell(self, sqlalchemy_table: Mock) -> Cell:
        return Cell(
            table=sqlalchemy_table,
            col_name=TestCell.COL_NAME,
            row_id=TestCell.ROW_ID,
            expected_type=str,
            val=TestCell.VAL
        )

    @pytest.fixture
    def int_val_cell(self, sqlalchemy_table: Mock) -> Cell:
        return Cell(
            table=sqlalchemy_table,
            col_name=TestCell.YEAR_COL_NAME,
            row_id=TestCell.ROW_ID,
            expected_type=int,
            val=TestCell.YEAR_VAL
        )

    def test_str(self, str_val_cell: Cell):
        # Do
        cell_str = str(str_val_cell)

        # Check
        assert str(TestCell.VAL) == cell_str

    def test_add_str_val(self, str_val_cell: Cell):
        # Do
        res = str_val_cell + TestCell.OTHER_STR_VAL

        # Check
        assert res == TestCell.VAL + TestCell.OTHER_STR_VAL

    def test_add_int_val(self, int_val_cell: Cell):
        # Do
        res = int_val_cell + TestCell.OTHER_INT_VAL

        # Check
        assert res == TestCell.YEAR_VAL + TestCell.OTHER_INT_VAL

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cell.update_cell')
    def test_set(self, mock_update_cell: Mock, mock_running_tool: Mock, str_val_cell: Cell):
        # Setup
        mock_type = Mock(spec=type, return_value=str(TestCell.OTHER_STR_VAL))
        str_val_cell.expected_type = mock_type

        # Do
        str_val_cell.set(TestCell.OTHER_STR_VAL)

        # Check
        # Check str was called on val to cast it
        mock_type.assert_called_with(TestCell.OTHER_STR_VAL)
        # Check cell's val was updated
        assert str_val_cell.val == str(TestCell.OTHER_STR_VAL)
        # Check update_cell was called
        mock_update_cell.assert_called_with(
            tool=mock_running_tool,
            table=str_val_cell.table,
            column_name=str_val_cell.col_name,
            row_id=str_val_cell.row_id,
            value=str(TestCell.OTHER_STR_VAL)
        )

    def test_set_type_cast_fails(self, str_val_cell: Cell):
        # Setup
        mock_type = Mock(spec=type, side_effect=ValueError)
        str_val_cell.expected_type = mock_type

        # Do, Check
        with pytest.raises(CNLError,
                           match=f"An error occurred while trying to cast {TestCell.OTHER_STR_VAL} to {mock_type}"):
            str_val_cell.set(TestCell.OTHER_STR_VAL)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cell.update_cell')
    def test_lshift(self, mock_update_cell: Mock, mock_running_tool: Mock, str_val_cell: Cell):
        # lshift for cells is syntactic sugar for set, so just check for the same things

        # Setup
        mock_type = Mock(spec=type, return_value=str(TestCell.OTHER_STR_VAL))
        str_val_cell.expected_type = mock_type

        # Do
        str_val_cell << TestCell.OTHER_STR_VAL

        # Check
        # Check str was called on val to cast it
        mock_type.assert_called_with(TestCell.OTHER_STR_VAL)
        # Check cell's val was updated
        assert str_val_cell.val == str(TestCell.OTHER_STR_VAL)
        # Check update_cell was called
        mock_update_cell.assert_called_with(
            tool=mock_running_tool,
            table=str_val_cell.table,
            column_name=str_val_cell.col_name,
            row_id=str_val_cell.row_id,
            value=str(TestCell.OTHER_STR_VAL)
        )

    @pytest.fixture
    def str_val_cell_part_two(self, sqlalchemy_table: Mock) -> Cell:
        return Cell(
            table=sqlalchemy_table,
            col_name=TestCell.COL_NAME,
            row_id=TestCell.ANOTHER_ROW_ID,
            expected_type=str,
            val=TestCell.OTHER_STR_VAL
        )

    def test_eq_other_is_a_cell(self, str_val_cell: Cell, str_val_cell_part_two: Cell):
        # Do
        res = str_val_cell == str_val_cell_part_two

        # Check
        assert res == (TestCell.VAL == TestCell.OTHER_STR_VAL)

    def test_eq_other_is_literal(self, str_val_cell: Cell):
        # Do
        res = str_val_cell == TestCell.VAL

        # Check
        assert res

    @pytest.fixture
    def int_val_cell_electric_boogaloo(self, sqlalchemy_table: Mock) -> Cell:
        return Cell(
            table=sqlalchemy_table,
            col_name=TestCell.YEAR_COL_NAME,
            row_id=TestCell.ANOTHER_ROW_ID,
            expected_type=int,
            val=TestCell.OTHER_INT_VAL
        )

    def test_mul_other_is_a_cell(self, int_val_cell: Cell, int_val_cell_electric_boogaloo: Cell):
        # Do
        res = int_val_cell * int_val_cell_electric_boogaloo

        # Check
        assert res == TestCell.YEAR_VAL * TestCell.OTHER_INT_VAL

    def test_mul_other_is_a_literal(self, int_val_cell: Cell):
        # Do
        res = int_val_cell * TestCell.OTHER_INT_VAL

        # Check
        assert res == TestCell.YEAR_VAL * TestCell.OTHER_INT_VAL

    def test_get_val_type_cast_fails(self, str_val_cell: Cell):
        # Setup
        mock_type = Mock(spec=type, side_effect=Exception)
        str_val_cell.expected_type = mock_type

        # Do, Check
        with pytest.raises(CNLError, match=f"An error occurred while trying to cast {TestCell.VAL} to {mock_type}"):
            str_val_cell.get_val()
