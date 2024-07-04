import typing

import pandas as pd
import sqlalchemy

import coolNewLanguage.src.tool as toolModule
import coolNewLanguage.src.util.sql_alch_csv_utils as sql_alch_csv_utils


class Tables:
    """
    A class to represent the tables in a tool.
    Changes to underlying tables are cached until approvals are handled.
    Some notes on cached changes and ordering:
    If a table is added/modified and then deleted, then it is ultimately deleted.
    If a table is deleted and then added/modified, then it is ultimately added/modified.
    If a table is added/modified multiple times, then only the last change is saved.
    If a table is added/modified and then accessed, the modified version is returned.
    If a table is deleted and then accessed, a KeyError is raised.
    """
    __slots__ = ('_tables', '_tool', '_tables_to_save', '_tables_to_delete')

    def __init__(self, tool):
        if not isinstance(tool, toolModule.Tool):
            raise TypeError("Tool must be a Tool object")

        # Fetch existing table names
        insp = sqlalchemy.inspect(tool.db_engine)
        self._tables: list[str] = insp.get_table_names()

        self._tool: toolModule.Tool = tool
        self._tables_to_save: dict[str, pd.DataFrame] = {}
        self._tables_to_delete: set[str] = set()

    def __len__(self) -> int:
        return len(self._tables)

    def __getitem__(self, table_name: str) -> pd.DataFrame:
        """
        Returns the pandas DataFrame containing the corresponding table. If the requested table isn't found, raises a
        KeyError. If the table was slated to be added/modified, returns the cached modified version. If the table was
        slated to be deleted, raises a KeyError.
        :param table_name: A string representing the table name.
        :return:
        """
        if not isinstance(table_name, str):
            raise TypeError("Table name must be a string")

        if table_name in self._tables_to_delete:
            raise KeyError(f"Table {table_name} was deleted")

        if table_name not in self:
            raise KeyError(f"Table {table_name} not found")

        # If the table was slated to be added/modified, return the cached version
        if table_name in self._tables_to_save:
            return self._tables_to_save[table_name]

        return self._tool.get_table_dataframe(table_name)

    def __setitem__(self, table_name: str, value: pd.DataFrame):
        """
        Adds/updates a table in the tool. If the table was slated to be deleted, removes it from the deletion list. If
        the same table was slated to be added/modified, updates the cached version.
        :param table_name:
        :param value:
        :return:
        """
        if not isinstance(table_name, str):
            raise TypeError("Table name must be a string")
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Value must be a pandas DataFrame")

        # If the table was slated to be deleted, remove it from the deletion list
        self._tables_to_delete.discard(table_name)

        # Cache the change to save it after approvals are handled
        self._tables_to_save[table_name] = value

    def __delitem__(self, table_name: str):
        """
        Deletes a table from the tool. If the table was slated to be added/modified, removes it from the save list.
        :param table_name:
        :return:
        """
        if not isinstance(table_name, str):
            raise TypeError("Table name must be a string")

        if table_name not in self._tables:
            raise KeyError(f"Table {table_name} not found")

        # If the table was slated to be added/modified, remove it from the save list
        self._tables_to_save.pop(table_name, None)

        # Cache the table to be deleted
        self._tables_to_delete.add(table_name)

    def __iter__(self) -> typing.Iterator[str]:
        """
        Returns an iterator which iterates over the table names. Also iterates over the names of tables which are slated
        to be added to the underlying database. No guarantees are made as to the order of iteration.
        :return:
        """
        table_names = set(self._tables) | set(self._tables_to_save.keys())
        return iter(table_names)

    def __contains__(self, table_name: str) -> bool:
        if table_name in self._tables_to_delete:
            return False
        return table_name in self._tables or table_name in self._tables_to_save

    def _flush_changes(self):
        """
        Flushes the changes to the underlying database. Tables to be added or modified are updated to the tool's
        database, while tables to be deleted are dropped.
        :return:
        """
        with self._tool.db_engine.connect() as conn:
            for table_name, table in self._tables_to_save.items():
                table.to_sql(name=table_name, con=conn, if_exists='replace')

            for table_name in self._tables_to_delete:
                table = self._tool.get_table_from_table_name(table_name)
                table.drop(self._tool.db_engine)

    def get_table_names(self, only_user_tables: bool = True):
        """
        Returns the names of the tables in the tool.
        :param only_user_tables: If True, only returns the names of user-created tables.
        :return:
        """
        if not isinstance(only_user_tables, bool):
            raise TypeError("Expected only_user_tables to be a boolean")

        if only_user_tables:
            return list(filter(lambda table_name: not table_name.startswith('__'), self._tables))
        return self._tables

    def get_columns_of_table(self, table_name: str, only_user_columns: bool = True) -> list[str]:
        """
        Get the column names of the passed table
        :param table_name: The name of the table from which to get the column names
        :param only_user_columns: Whether the column names should be filtered to include only user columns
        :return: A list of column names
        """
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")
        if not isinstance(only_user_columns, bool):
            raise TypeError("Expected only_user_columns to be a boolean")

        if table_name not in self:
            raise KeyError(f"Table {table_name} not found")

        columns = self[table_name].columns.tolist()

        if only_user_columns:
            return sql_alch_csv_utils.filter_to_user_columns(columns)
        return columns
