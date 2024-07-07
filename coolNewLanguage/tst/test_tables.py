import random
from unittest.mock import Mock, MagicMock, patch, call

import pandas as pd
import pytest
import sqlalchemy

import coolNewLanguage.src.tool as tool
from coolNewLanguage.src.tables import Tables


class TestTables:

    TABLE_NAMES = ['table_1', 'table_2', 'table_3']

    @patch('coolNewLanguage.src.tables.sqlalchemy')
    def test_tables_happy_path(self, mock_sqlalchemy: Mock):
        # Setup
        mock_tool = Mock(spec=tool.Tool, db_engine=Mock())
        # Mock get_table_names
        mock_inspector = Mock()
        mock_sqlalchemy.inspect.return_value = mock_inspector
        mock_inspector.get_table_names.return_value = self.TABLE_NAMES

        # Do
        tables = Tables(mock_tool)

        # Check
        mock_sqlalchemy.inspect.assert_called_once_with(mock_tool.db_engine)
        mock_inspector.get_table_names.assert_called_once()

        assert tables._tables == {'table_1', 'table_2', 'table_3'}
        assert tables._tool == mock_tool
        assert tables._tables_to_save == {}
        assert tables._tables_to_delete == set()

    def test_tables_non_tool_tool(self):
        # Setup
        mock_tool = Mock()

        # Do/Check
        with pytest.raises(TypeError, match="Tool must be a Tool object"):
            Tables(mock_tool)

    @pytest.fixture
    @patch('coolNewLanguage.src.tables.sqlalchemy')
    def tables(self, mock_sqlalchemy: Mock) -> Tables:
        mock_tool = Mock(spec=tool.Tool, db_engine=Mock())

        tables = Tables(mock_tool)
        tables._tables = MagicMock()

        return tables

    def test_tables_len(self, tables: Tables):
        # Setup
        mock_length = random.randint(0, 1000)
        tables._tables.__len__.return_value = mock_length

        # Do, Check
        assert len(tables) == mock_length


    TABLE_NAME = "table_name"

    def test_tables_get_item_happy_path(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True

        mock_dataframe = Mock()
        mock_get_table_dataframe = Mock(return_value=mock_dataframe)
        tables._tool.get_table_dataframe = mock_get_table_dataframe

        # Do
        dataframe = tables[TestTables.TABLE_NAME]

        # Check
        assert dataframe == mock_dataframe
        mock_get_table_dataframe.assert_called_once_with(TestTables.TABLE_NAME)

    def test_tables_get_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            tables[None]

    def test_tables_get_item_table_not_found(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = False

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} not found"):
            tables[TestTables.TABLE_NAME]

    def test_tables_get_item_table_deleted(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} was deleted"):
            tables[TestTables.TABLE_NAME]

    def test_tables_table_in_tables_to_save(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        mock_dataframe = Mock()
        tables._tables_to_save[TestTables.TABLE_NAME] = mock_dataframe

        # Do
        dataframe = tables[TestTables.TABLE_NAME]

        # Check
        assert dataframe == mock_dataframe

    def test_tables_set_item_happy_path(self, tables: Tables):
        # Setup
        mock_dataframe = Mock(spec=pd.DataFrame)

        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do
        tables[TestTables.TABLE_NAME] = mock_dataframe

        # Check
        assert tables._tables_to_save[TestTables.TABLE_NAME] == mock_dataframe
        assert TestTables.TABLE_NAME not in tables._tables_to_delete

    def test_tables_set_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            tables[Mock()] = Mock(spec=pd.DataFrame)

    def test_tables_set_item_non_dataframe_value(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Value must be a pandas DataFrame"):
            tables[TestTables.TABLE_NAME] = Mock()

    def test_tables_del_item_happy_path(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        tables._tables_to_save[TestTables.TABLE_NAME] = Mock()

        # Do
        del tables[TestTables.TABLE_NAME]

        # Check
        assert TestTables.TABLE_NAME not in tables._tables_to_save
        assert TestTables.TABLE_NAME in tables._tables_to_delete

    def test_tables_del_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            del tables[Mock()]

    def test_tables_del_item_table_not_found(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = False

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} not found"):
            del tables[TestTables.TABLE_NAME]

    def test_tables_iter(self, tables: Tables):
        # Setup
        tables._tables = ['1', '2', '3']
        tables._tables_to_save = {'4': Mock(), '5': Mock()}

        # Do
        table_names = set(iter(tables))

        # Check
        assert table_names == {'1', '2', '3', '4', '5'}

    def test_tables_contains(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True

        # Do/Check
        assert TestTables.TABLE_NAME in tables

    def test_tables_contains_table_in_tables_to_save(self, tables: Tables):
        # Setup
        tables._tables_to_save[TestTables.TABLE_NAME] = Mock()

        # Do/Check
        assert TestTables.TABLE_NAME in tables

    def test_tables_contains_table_deleted(self, tables: Tables):
        # Setup
        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do/Check
        assert TestTables.TABLE_NAME not in tables

    def test_save_table_with_connection_happy_path(self, tables: Tables):
        # Setup
        mock_connection = Mock(spec=sqlalchemy.Connection)
        mock_dataframe = Mock(spec=pd.DataFrame)

        # Do
        tables._save_table(TestTables.TABLE_NAME, mock_dataframe, mock_connection)

        # Check
        mock_dataframe.to_sql.assert_called_once_with(
            name=TestTables.TABLE_NAME,
            con=mock_connection,
            if_exists='replace'
        )

        tables._tables.add.assert_called_once_with(TestTables.TABLE_NAME)

    def test_save_table_no_connection_happy_path(self, tables: Tables):
        # Setup
        # Mock tables._tool._db_engine.connect
        mock_connection = MagicMock()
        tables._tool.db_engine.connect.return_value = mock_connection
        mock_dataframe = Mock(spec=pd.DataFrame)

        # Do
        tables._save_table(TestTables.TABLE_NAME, mock_dataframe)

        # Check
        mock_dataframe.to_sql.assert_called_once_with(
            name=TestTables.TABLE_NAME,
            con=mock_connection.__enter__.return_value,
            if_exists='replace'
        )

        tables._tables.add.assert_called_once_with(TestTables.TABLE_NAME)

    def test_save_table_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected table_name to be a string"):
            tables._save_table(Mock(), Mock(spec=pd.DataFrame))

    def test_save_table_non_dataframe_df(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected df to be a pandas DataFrame"):
            tables._save_table(TestTables.TABLE_NAME, Mock())

    def test_save_table_non_connection_conn(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected conn to be a sqlalchemy Connection object or None"):
            tables._save_table(TestTables.TABLE_NAME, Mock(spec=pd.DataFrame), Mock())

    def test_tables_delete_table_happy_path(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        # Mock tables._tool.get_table_from_table_name
        mock_table = Mock()
        tables._tool.get_table_from_table_name.return_value = mock_table

        # Do
        tables._delete_table(TestTables.TABLE_NAME)

        # Check
        tables._tool.get_table_from_table_name.assert_called_once_with(TestTables.TABLE_NAME)
        mock_table.drop.assert_called_once_with(tables._tool.db_engine)
        tables._tables.remove.assert_called_once_with(TestTables.TABLE_NAME)

    def test_tables_delete_table_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected table_name to be a string"):
            tables._delete_table(Mock())

    def test_tables_delete_table_table_name_not_in_tables(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = False

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} not found"):
            tables._delete_table(TestTables.TABLE_NAME)

    @patch('coolNewLanguage.src.tables.Tables._delete_table')
    @patch('coolNewLanguage.src.tables.Tables._save_table')
    def test_tables_flush_changes(self, mock_save_table: MagicMock, mock_delete_table: MagicMock, tables: Tables):
        # Setup
        mock_connection = MagicMock()
        tables._tool.db_engine.connect.return_value = mock_connection
        tables._tables_to_save = {'1': Mock(), '2': Mock()}
        tables._tables_to_delete = {'3', '4'}
        tables._tables = {'1', '2', '3', '4'}
        # Mock tables._tool._get_table_from_table_name
        mock_table = Mock()
        tables._tool.get_table_from_table_name.return_value = mock_table

        # Do
        tables._flush_changes()

        # Check
        mock_save_table.assert_has_calls(
            [
                call('1', tables._tables_to_save['1'], mock_connection.__enter__.return_value),
                call('2', tables._tables_to_save['2'], mock_connection.__enter__.return_value)
            ],
            any_order=True
        )

        mock_delete_table.assert_has_calls([call('3'), call('4')], any_order=True)

    def test_clear_changes(self, tables: Tables):
        # Setup
        tables._tables_to_save = {'1': Mock(), '2': Mock()}
        tables._tables_to_delete = {'3', '4'}

        # Do
        tables._clear_changes()

        # Check
        assert tables._tables_to_save == {}
        assert tables._tables_to_delete == set()

    def test_tables_get_table_names_happy_path(self, tables: Tables):
        # Setup
        mock_table_names = ['table_1', '__table_2', 'table_3', '__table_4']
        tables._tables = mock_table_names

        # Do
        table_names = tables.get_table_names()

        # Check
        assert table_names == ['table_1', 'table_3']


    def test_tables_get_table_names_all_tables(self, tables: Tables):
        # Setup
        mock_table_names = ['table_1', '__table_2', 'table_3', '__table_4']
        tables._tables = mock_table_names

        # Do
        table_names = tables.get_table_names(False)

        # Check
        assert table_names == mock_table_names

    def test_tables_get_table_names_non_bool_only_user_tables(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected only_user_tables to be a boolean"):
            tables.get_table_names(Mock())

    @patch('coolNewLanguage.src.tables.sql_alch_csv_utils')
    def test_get_columns_of_table_happy_path(self, mock_sql_alch_csv_utils: Mock, tables: Tables):
        # Setup
        mock_dataframe = Mock(spec=pd.DataFrame)
        mock_columns = ['col1', 'col2', 'col3']
        mock_dataframe.columns.tolist.return_value = mock_columns
        tables['table_name'] = mock_dataframe

        mock_sql_alch_csv_utils.filter_to_user_columns.return_value = mock_columns[:1]

        # Do
        columns = tables.get_columns_of_table('table_name')

        # Check
        assert columns == mock_columns[:1]

    def test_get_columns_of_table_all_columns(self, tables: Tables):
        # Setup
        mock_dataframe = Mock(spec=pd.DataFrame)
        mock_columns = ['col1', 'col2', 'col3']
        mock_dataframe.columns.tolist.return_value = mock_columns
        tables['table_name'] = mock_dataframe

        # Do
        columns = tables.get_columns_of_table('table_name', False)

        # Check
        assert columns == mock_columns

    def test_get_columns_of_table_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected table_name to be a string"):
            tables.get_columns_of_table(Mock())

    def test_get_columns_of_table_non_bool_only_user_columns(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Expected only_user_columns to be a boolean"):
            tables.get_columns_of_table('table_name', Mock())

    def test_get_columns_of_table_table_not_found(self, tables: Tables):
        # Do/Check
        with pytest.raises(KeyError, match="Table table_name not found"):
            tables.get_columns_of_table('table_name')