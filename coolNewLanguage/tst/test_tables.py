import random
from unittest.mock import Mock, MagicMock

import pandas as pd
import pytest

import coolNewLanguage.src.tool as tool
from coolNewLanguage.src.tables import Tables


class TestTables:

    def test_table_happy_path(self):
        # Setup
        mock_tool = Mock(spec=tool.Tool)
        mock_table_names = Mock()
        mock_tool.get_table_names = Mock(return_value=mock_table_names)

        # Do
        tables = Tables(mock_tool)

        # Check
        assert tables._tables == mock_table_names
        assert tables._tool == mock_tool
        assert tables._tables_to_save == {}
        assert tables._tables_to_delete == set()

    def test_table_non_tool_tool(self):
        # Setup
        mock_tool = Mock()

        # Do/Check
        with pytest.raises(TypeError, match="Tool must be a Tool object"):
            Tables(mock_tool)

    @pytest.fixture
    def tables(self) -> Tables:
        mock_tool = Mock(spec=tool.Tool)
        mock_table_names = MagicMock()
        mock_tool.get_table_names = Mock(return_value=mock_table_names)

        return Tables(mock_tool)

    def test_table_len(self, tables: Tables):
        # Setup
        mock_length = random.randint(0, 1000)
        tables._tables.__len__.return_value = mock_length

        # Do, Check
        assert len(tables) == mock_length


    TABLE_NAME = "table_name"

    def test_table_get_item_happy_path(self, tables: Tables):
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

    def test_table_get_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            tables[None]

    def test_table_get_item_table_not_found(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = False

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} not found"):
            tables[TestTables.TABLE_NAME]

    def test_table_get_item_table_deleted(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} was deleted"):
            tables[TestTables.TABLE_NAME]

    def test_table_table_in_tables_to_save(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        mock_dataframe = Mock()
        tables._tables_to_save[TestTables.TABLE_NAME] = mock_dataframe

        # Do
        dataframe = tables[TestTables.TABLE_NAME]

        # Check
        assert dataframe == mock_dataframe

    def test_table_set_item_happy_path(self, tables: Tables):
        # Setup
        mock_dataframe = Mock(spec=pd.DataFrame)

        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do
        tables[TestTables.TABLE_NAME] = mock_dataframe

        # Check
        assert tables._tables_to_save[TestTables.TABLE_NAME] == mock_dataframe
        assert TestTables.TABLE_NAME not in tables._tables_to_delete

    def test_table_set_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            tables[Mock()] = Mock(spec=pd.DataFrame)

    def test_table_set_item_non_dataframe_value(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Value must be a pandas DataFrame"):
            tables[TestTables.TABLE_NAME] = Mock()

    def test_table_del_item_happy_path(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True
        tables._tables_to_save[TestTables.TABLE_NAME] = Mock()

        # Do
        del tables[TestTables.TABLE_NAME]

        # Check
        assert TestTables.TABLE_NAME not in tables._tables_to_save
        assert TestTables.TABLE_NAME in tables._tables_to_delete

    def test_table_del_item_non_string_table_name(self, tables: Tables):
        # Do/Check
        with pytest.raises(TypeError, match="Table name must be a string"):
            del tables[Mock()]

    def test_table_del_item_table_not_found(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = False

        # Do/Check
        with pytest.raises(KeyError, match=f"Table {TestTables.TABLE_NAME} not found"):
            del tables[TestTables.TABLE_NAME]

    def test_table_iter(self, tables: Tables):
        # Setup
        tables._tables = ['1', '2', '3']
        tables._tables_to_save = {'4': Mock(), '5': Mock()}

        # Do
        table_names = set(iter(tables))

        # Check
        assert table_names == {'1', '2', '3', '4', '5'}

    def test_table_contains(self, tables: Tables):
        # Setup
        tables._tables.__contains__.return_value = True

        # Do/Check
        assert TestTables.TABLE_NAME in tables

    def test_table_contains_table_in_tables_to_save(self, tables: Tables):
        # Setup
        tables._tables_to_save[TestTables.TABLE_NAME] = Mock()

        # Do/Check
        assert TestTables.TABLE_NAME in tables

    def test_table_contains_table_deleted(self, tables: Tables):
        # Setup
        tables._tables_to_delete.add(TestTables.TABLE_NAME)

        # Do/Check
        assert TestTables.TABLE_NAME not in tables
