import typing

import pandas as pd

import coolNewLanguage.src.tool
import coolNewLanguage.src.tool as toolModule
import coolNewLanguage.src.util.db_utils as db_utils


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
        self._tables: list[str] = tool.get_table_names()
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

        if table_name not in self._tables:
            raise KeyError(f"Table {table_name} not found")

        if table_name in self._tables_to_delete:
            raise KeyError(f"Table {table_name} was deleted")

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
