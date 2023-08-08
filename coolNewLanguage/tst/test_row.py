from unittest.mock import Mock, patch

import pytest
import sqlalchemy

import coolNewLanguage.src.cnl_type.cnl_type
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME
from coolNewLanguage.tst.cnl_type.cnl_type_test_utils import MyFirstType


class TestRow:
    ROW_ID_1 = 1
    ROW_ID_2 = 2
    TABLE_NAME_1 = "Mascots"
    TABLE_NAME_2 = "Universities"
    NAME_COLUMN = "Names"
    INVALID_COLUMN_NAME = "not a real column"
    OSKI = "Oski"
    OSKI_BEAR = "Oski Bear"
    ROW_DICT_1 = {
        DB_INTERNAL_COLUMN_ID_NAME: ROW_ID_1,
        NAME_COLUMN: OSKI
    }
    SCHOOL_NAME_COLUMN = "School name"
    BERKELEY = "Cal"
    ROW_DICT_2 = {
        DB_INTERNAL_COLUMN_ID_NAME: ROW_ID_2,
        SCHOOL_NAME_COLUMN: BERKELEY
    }
    SQLALCHEMY_ROW_1 = Mock(spec=sqlalchemy.Row)
    SQLALCHEMY_ROW_2 = Mock(spec=sqlalchemy.Row)
    SQLALCHEMY_TABLE_1 = Mock(spec=sqlalchemy.Table)
    SQLALCHEMY_TABLE_2 = Mock(spec=sqlalchemy.Table)
    LINK_META_ID = 58
    LINK = Mock(spec=Link, get_link_meta_id=Mock(return_value=LINK_META_ID))
    LINK_ID = 6

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        process.handling_post = False

        yield

        process.handling_post = True

    @pytest.fixture
    def row_1(self) -> Row:
        TestRow.SQLALCHEMY_ROW_1._asdict.return_value = TestRow.ROW_DICT_1
        TestRow.SQLALCHEMY_TABLE_1.name = TestRow.TABLE_NAME_1
        return Row(table=TestRow.SQLALCHEMY_TABLE_1, sqlalchemy_row=TestRow.SQLALCHEMY_ROW_1)

    @pytest.fixture
    def row_2(self) -> Row:
        TestRow.SQLALCHEMY_ROW_2._asdict.return_value = TestRow.ROW_DICT_2
        TestRow.SQLALCHEMY_TABLE_2.name = TestRow.TABLE_NAME_2
        return Row(table=TestRow.SQLALCHEMY_TABLE_2, sqlalchemy_row=TestRow.SQLALCHEMY_ROW_2)

    def test_row_happy_path(self):
        # Setup
        sqlalchemy_table = Mock(spec=sqlalchemy.Table)
        sqlalchemy_row = Mock(spec=sqlalchemy.Row)
        sqlalchemy_row._asdict.return_value = TestRow.ROW_DICT_1

        # Do
        row = Row(table=sqlalchemy_table, sqlalchemy_row=sqlalchemy_row)

        # Check
        # Check row_mapping is set to sqlalchemy_row's _asdict
        assert row.row_mapping == TestRow.ROW_DICT_1
        # Check table set properly
        assert row.table == sqlalchemy_table
        # Check row_id set properly
        assert row.row_id == TestRow.ROW_ID_1
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

    def test_getitem_item_is_string_cell_not_in_cell_mapping(self, row_1):
        # Setup
        # Check cell not in row's cell_mapping
        assert TestRow.NAME_COLUMN not in row_1.cell_mapping

        # Do
        cell1 = row_1[TestRow.NAME_COLUMN]
        cell2 = row_1.__getitem__(TestRow.NAME_COLUMN)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check cell now in row's cell_mapping
        assert TestRow.NAME_COLUMN in row_1.cell_mapping
        # Check values of Cell
        expected_cell_val = Cell(
            table=row_1.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row_1.row_id,
            expected_type=None,
            val=TestRow.OSKI
        )
        assert cell1 == expected_cell_val

    def test_getitem_item_is_column_selector_component_cell_not_in_cell_mapping(self, row_1):
        # Setup
        # Check cell not in row's cell_mapping
        assert TestRow.NAME_COLUMN not in row_1.cell_mapping
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_val_type = mock_type

        # Do
        cell1 = row_1[column_selector_component]
        cell2 = row_1.__getitem__(column_selector_component)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check cell now in row's cell_mapping
        assert TestRow.NAME_COLUMN in row_1.cell_mapping
        # Check values of Cell
        expected_cell_val = Cell(
            table=row_1.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row_1.row_id,
            expected_type=mock_type,
            val=TestRow.OSKI
        )
        assert cell1 == expected_cell_val

    def test_getitem_item_is_string_cell_already_in_cell_mapping(self, row_1):
        # Setup
        mock_cell = Mock(spec=Cell)
        row_1.cell_mapping[TestRow.NAME_COLUMN] = mock_cell

        # Do
        cell1 = row_1[TestRow.NAME_COLUMN]
        cell2 = row_1.__getitem__(TestRow.NAME_COLUMN)

        # Check
        # Check that both ways of getting cells return the same thing
        assert cell1 == cell2
        # Check values of Cell
        assert cell1 == mock_cell

    def test_getitem_item_is_not_string_or_column_selector_component(self, row_1):
        # Do, Check
        with pytest.raises(TypeError, match="Expected item to be a string or ColumnSelectorComponent"):
            _ = row_1[Mock()]

    @patch('coolNewLanguage.src.row.Cell')
    def test_setitem_key_is_string_happy_path(self, mock_cell: Mock, row_1):
        # Setup
        # Check that key is not in cell_mapping
        assert TestRow.NAME_COLUMN not in row_1.cell_mapping
        # Mock the cell instance that is created for row's cell_mapping
        mock_cell_instance = Mock(spec=Cell)
        mock_cell.return_value = mock_cell_instance
        # Mock cell.set so we can verify the call later
        mock_cell_set = Mock()
        mock_cell_instance.set = mock_cell_set

        # Do
        row_1[TestRow.NAME_COLUMN] = TestRow.OSKI_BEAR

        # Check
        # Check that key is now set in cell_mapping
        assert TestRow.NAME_COLUMN in row_1.cell_mapping
        # Check Cell was instantiated with appropriate arguments
        mock_cell.assert_called_with(
            table=row_1.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row_1.row_id,
            expected_type=None,
            val=row_1.row_mapping[TestRow.NAME_COLUMN]
        )
        # Check that cell.set was called
        mock_cell_set.assert_called_with(TestRow.OSKI_BEAR)

    @patch('coolNewLanguage.src.row.Cell')
    def test_setitem_key_is_column_selector_component_happy_path(self, mock_cell: Mock, row_1):
        # Setup
        # Create mock column selector to use
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_type = mock_type
        # Check that key is not in cell_mapping
        assert TestRow.NAME_COLUMN not in row_1.cell_mapping
        # Mock the cell instance that is created for row's cell_mapping
        mock_cell_instance = Mock(spec=Cell)
        mock_cell.return_value = mock_cell_instance
        mock_cell_instance.expected_type = Mock(spec=type)
        # Mock cell.set so we can verify the call later
        mock_cell_set = Mock()
        mock_cell_instance.set = mock_cell_set

        # Do
        row_1[column_selector_component] = TestRow.OSKI_BEAR

        # Check
        # Check that key is now set in cell_mapping
        assert TestRow.NAME_COLUMN in row_1.cell_mapping
        # Check Cell was instantiated with appropriate arguments
        mock_cell.assert_called_with(
            table=row_1.table,
            col_name=TestRow.NAME_COLUMN,
            row_id=row_1.row_id,
            expected_type=mock_type,
            val=row_1.row_mapping[TestRow.NAME_COLUMN]
        )
        # Check that cell.set was called
        mock_cell_set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_string_key_in_cell_mapping_happy_path(self, row_1):
        # Setup
        # Put a mock cell in row's cell_mapping
        mock_cell = Mock(spec=Cell)
        row_1.cell_mapping[TestRow.NAME_COLUMN] = mock_cell

        # Do
        row_1[TestRow.NAME_COLUMN] = TestRow.OSKI_BEAR

        # Check
        # Check that the mock cell's set method was called
        mock_cell.set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_column_selector_component_key_in_cell_mapping_happy_path(self, row_1):
        # Setup
        # Put a mock cell in row's cell_mapping
        mock_cell = Mock(spec=Cell)
        # Set mock_cell's type to None to check if it's updated later
        mock_cell.expected_type = None
        row_1.cell_mapping[TestRow.NAME_COLUMN] = mock_cell
        # Create mock column selector to use
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.NAME_COLUMN
        mock_type = Mock(spec=type)
        column_selector_component.expected_type = mock_type

        # Do
        row_1[column_selector_component] = TestRow.OSKI_BEAR

        # Check
        # Check that the mock cell's expected type was updated
        assert mock_cell.expected_type == mock_type
        # Check that the mock cell's set method was called
        mock_cell.set.assert_called_with(TestRow.OSKI_BEAR)

    def test_setitem_key_is_string_key_is_not_valid_column_name(self, row_1):
        # Do, Check
        with pytest.raises(ValueError, match=f"Key {TestRow.INVALID_COLUMN_NAME} is not a valid column name"):
            row_1[TestRow.INVALID_COLUMN_NAME] = TestRow.OSKI

    def test_setitem_key_is_column_selector_component_key_is_not_valid_column_name(self, row_1):
        # Setup
        column_selector_component = Mock(spec=ColumnSelectorComponent)
        column_selector_component.emulated_column = TestRow.INVALID_COLUMN_NAME
        column_selector_component.expected_type = None

        # Do, Check
        with pytest.raises(ValueError, match=f"Key {TestRow.INVALID_COLUMN_NAME} is not a valid column name"):
            row_1[column_selector_component] = TestRow.OSKI

    def test_setitem_key_is_not_string_or_column_selector_component(self, row_1):
        # Do, Check
        with pytest.raises(TypeError, match="Expected key to be a string or a ColumnSelectorComponent"):
            row_1[Mock()] = Mock()

    def test_keys_happy_path(self, row_1):
        # Do, Check
        assert row_1.keys() == TestRow.ROW_DICT_1.keys()

    def test_contains_happy_path(self, row_1):
        # Do, Check
        assert TestRow.NAME_COLUMN in row_1
        assert TestRow.INVALID_COLUMN_NAME not in row_1

    def test_iter_happy_path(self, row_1):
        # Do, Check
        vals = []
        for val in row_1:
            vals.append(val)
        assert vals == [TestRow.ROW_ID_1, TestRow.OSKI]

    @patch.object(coolNewLanguage.src.cnl_type.cnl_type.CNLType, 'from_row')
    def test_cast_to_type_happy_path(self, mock_from_row: Mock, row_1):
        # Setup
        # Mock CNLType.from_row
        mock_my_first_type = Mock(spec=MyFirstType)
        mock_from_row.return_value = mock_my_first_type

        # Do
        my_first_type = row_1.cast_to_type(MyFirstType)

        # Check
        # Check from_row was called as expected
        mock_from_row.assert_called_with(cnl_type=MyFirstType, row=row_1)
        # Check return value
        assert my_first_type == mock_my_first_type

    def test_cast_to_type_cnl_type_is_not_cnl_type_subclass(self, row_1):
        with pytest.raises(TypeError, match="Expected cnl_type to be a subclass of CNLType"):
            row_1.cast_to_type(Row)

    @patch('coolNewLanguage.src.row.register_new_link')
    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.row.get_link_id')
    def test_link_dst_is_row(
            self,
            mock_get_link_id: Mock,
            mock_running_tool: Mock,
            mock_register_new_link: Mock,
            row_1: Row,
            row_2: Row
    ):
        # Setup
        process.handling_post = True
        # get_link_id should return None
        mock_get_link_id.return_value = None
        mock_register_new_link.return_value = TestRow.LINK_ID

        # Do
        link_id = row_1.link(link_dst=row_2, link_metatype=TestRow.LINK)

        # Check
        # Check that get_link_id was called
        mock_get_link_id.assert_called_with(
            tool=mock_running_tool,
            link_meta_id=TestRow.LINK_META_ID,
            src_table_name=TestRow.TABLE_NAME_1,
            src_row_id=TestRow.ROW_ID_1,
            dst_table_name=TestRow.TABLE_NAME_2,
            dst_row_id=TestRow.ROW_ID_2
        )
        # Check that register_new_link was called
        mock_register_new_link.assert_called_with(
            tool=mock_running_tool,
            link_meta_id=TestRow.LINK_META_ID,
            src_table_name=TestRow.TABLE_NAME_1,
            src_row_id=TestRow.ROW_ID_1,
            dst_table_name=TestRow.TABLE_NAME_2,
            dst_row_id=TestRow.ROW_ID_2
        )
        assert link_id == TestRow.LINK_ID

    @patch('coolNewLanguage.src.row.register_new_link')
    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.row.get_link_id')
    def test_link_dst_is_cnl_type(
            self,
            mock_get_link_id: Mock,
            mock_running_tool: Mock,
            mock_register_new_link: Mock,
            row_1: Row,
            row_2: Row
    ):
        # Setup
        process.handling_post = True
        cnl_type = Mock(spec=CNLType, _hls_backing_row=row_2)
        # get_link_id should return None
        mock_get_link_id.return_value = None
        mock_register_new_link.return_value = TestRow.LINK_ID

        # Do
        link_id = row_1.link(link_dst=cnl_type, link_metatype=TestRow.LINK)

        # Check
        # Check that get_link_id was called
        mock_get_link_id.assert_called_with(
            tool=mock_running_tool,
            link_meta_id=TestRow.LINK_META_ID,
            src_table_name=TestRow.TABLE_NAME_1,
            src_row_id=TestRow.ROW_ID_1,
            dst_table_name=TestRow.TABLE_NAME_2,
            dst_row_id=TestRow.ROW_ID_2
        )
        # Check that register_new_link was called
        mock_register_new_link.assert_called_with(
            tool=mock_running_tool,
            link_meta_id=TestRow.LINK_META_ID,
            src_table_name=TestRow.TABLE_NAME_1,
            src_row_id=TestRow.ROW_ID_1,
            dst_table_name=TestRow.TABLE_NAME_2,
            dst_row_id=TestRow.ROW_ID_2
        )
        assert link_id == TestRow.LINK_ID

    @patch('coolNewLanguage.src.row.register_new_link')
    @patch('coolNewLanguage.src.row.get_link_id')
    def test_link_dst_is_cnl_type_has_no_backing_row(
            self,
            mock_get_link_id: Mock,
            mock_register_new_link: Mock,
            row_1: Row
    ):
        # Setup
        process.handling_post = True
        cnl_type = Mock(spec=CNLType, _hls_backing_row= None)

        # Do
        link_id = row_1.link(link_dst=cnl_type, link_metatype=TestRow.LINK)

        # Check
        # Check that get_link_id and register_new_link weren't called
        mock_get_link_id.assert_not_called()
        mock_register_new_link.assert_not_called()
        assert link_id is None

    @patch('coolNewLanguage.src.row.register_new_link')
    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.row.get_link_id')
    def test_link_link_already_exists(
            self,
            mock_get_link_id: Mock,
            mock_running_tool: Mock,
            mock_register_new_link: Mock,
            row_1: Row,
            row_2: Row
    ):
        # Setup
        process.handling_post = True
        mock_get_link_id.return_value = TestRow.LINK_ID

        # Do
        link_id = row_1.link(link_dst=row_2, link_metatype=TestRow.LINK)

        # Check
        # Check that get_link_id was called
        mock_get_link_id.assert_called_with(
            tool=mock_running_tool,
            link_meta_id=TestRow.LINK_META_ID,
            src_table_name=TestRow.TABLE_NAME_1,
            src_row_id=TestRow.ROW_ID_1,
            dst_table_name=TestRow.TABLE_NAME_2,
            dst_row_id=TestRow.ROW_ID_2
        )
        # Check that register_new_link wasn't called
        mock_register_new_link.assert_not_called()
        assert link_id == TestRow.LINK_ID

    @patch('coolNewLanguage.src.row.register_new_link')
    @patch('coolNewLanguage.src.row.get_link_id')
    def test_link_not_handling_post(
            self,
            mock_get_link_id: Mock,
            mock_register_new_link: Mock,
            row_1: Row,
            row_2: Row
    ):
        # Do
        link_id = row_1.link(link_dst=row_2, link_metatype=TestRow.LINK)

        # Check
        # Check that get_link_id and register_new_link weren't called
        mock_get_link_id.assert_not_called()
        mock_register_new_link.assert_not_called()
        assert link_id is None
