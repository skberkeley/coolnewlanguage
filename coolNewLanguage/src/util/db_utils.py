from pathlib import Path

import sqlalchemy

from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.tool import Tool
from typing import List, Tuple, Any, Iterator

from coolNewLanguage.src.util.sql_alch_csv_utils import sqlalchemy_table_from_csv_file, \
    sqlalchemy_insert_into_table_from_csv_file, filter_to_user_columns, DB_INTERNAL_COLUMN_ID_NAME


def create_table_from_csv(table_name: UserInputComponent, csv_file: FileUploadComponent, has_header: bool = True) -> sqlalchemy.Table:
    """
    Create a table in the database of the tool, using the csv file as the source for the data
    :param table_name: The name to use for the table being inserted
    :param csv_file: The csv file to use as the data source
    :param tool: The tool whose database the data will be inserted into
    :param has_header: Whether the passed csv file has a header or not
    :return: The created table
    """
    if not isinstance(table_name, UserInputComponent):
        raise TypeError("Expected a User Input for table name")
    if table_name.value is None:
        raise ValueError("Expected User Input to have a value for table name")
    if not isinstance(table_name.value, str):
        raise ValueError("Expected User Input value to be a string for table name")
    if not isinstance(csv_file, FileUploadComponent):
        raise TypeError("Expected a File Upload for csv file")
    if csv_file.value is None:
        raise ValueError("Expected File Upload to have a value for csv file")
    if not isinstance(csv_file.value, Path):
        raise ValueError("Expected File Upload value to be a Path to a file")
    if not isinstance(has_header, bool):
        raise TypeError("Expected a bool for has_header")

    # create table
    tool = process.running_tool
    metadata_obj = tool.db_metadata_obj
    with open(csv_file.value) as f:
        table = sqlalchemy_table_from_csv_file(table_name.value, f, metadata_obj, has_header)
    metadata_obj.create_all(tool.db_engine)
    # insert data
    with open(csv_file.value) as f:
        insert_stmt = sqlalchemy_insert_into_table_from_csv_file(table, f, has_header)
    with tool.db_engine.connect() as conn:
        conn.execute(insert_stmt)
        conn.commit()

    return table


def get_table_names_from_tool(tool: Tool) -> List[str]:
    """
    Get the names of the database tables associated with the passed table
    :param tool: The Tool from which to get associated table names
    :return: A list of table names
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected a Tool for tool")

    engine = tool.db_engine
    insp = sqlalchemy.inspect(engine)
    return insp.get_table_names()


def get_column_names_from_table_name(tool: Tool, table_name: str) -> List[str]:
    """
    Get the column names of the passed table
    :param tool: The Tool with which the table is associated
    :param table_name: The name of the table from which to get the column names
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected a Tool for tool")
    if not isinstance(table_name, str):
        raise TypeError("Expected a string for table_name")

    engine = tool.db_engine
    insp: sqlalchemy.Inspector = sqlalchemy.inspect(engine)

    if not insp.has_table(table_name):
        raise ValueError("The passed tool does not have an associated table with the passed name")

    columns = [str(col["name"]) for col in insp.get_columns(table_name=table_name)]
    return filter_to_user_columns(columns)


def get_table_from_table_name(tool: Tool, table_name: str) -> sqlalchemy.Table:
    """
    Get the sqlaclchemy Table which has the given name associated with the passed Tool
    Reflect the table using the engine associated with the Tool
    :param tool: The Tool from which to get the sqlalchemy table
    :param table_name: The name of the table which we try to get
    :return: The Table with matching name
    """
    engine = tool.db_engine
    insp: sqlalchemy.Inspector = sqlalchemy.inspect(engine)

    if not insp.has_table(table_name):
        raise ValueError("The passed tool does not have an associated table with the passed name")

    table = sqlalchemy.Table(table_name, tool.db_metadata_obj)
    insp.reflect_table(table, None)

    return table


def iterate_over_column(tool: Tool, table: sqlalchemy.Table, column_name: str) -> Iterator[Tuple[int, Any]]:
    """
    Iterate over the column with the passed column
    :param tool: The tool containing the associated table
    :param table: The sqlalchemy Table containing the column of interest
    :param column_name: The name of the column to iterate over
    :return: Yields a tuple of form (row_id, value)
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected table to be a sqlalchemy Table")
    if not isinstance(column_name, str):
        raise TypeError("Expected column name to be a string")

    engine = tool.db_engine
    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[column_name]

    query = sqlalchemy.select(id_column, target_column)
    with engine.connect() as conn:
        query_result = conn.execute(query)
    yield from query_result


def update_cell(tool: Tool, table: sqlalchemy.Table, column_name: str, row_id: int, value: Any):
    """
    Update the given cell, identified by the table_name, column_name and row_id, to the passed value
    :param tool: The Tool which owns the table with the cell to be updated
    :param table: The table with the cell to be updated
    :param column_name: The name of the column containing the cell to be updated
    :param row_id: The row containing the cell to be updated
    :param value: The value to update the cell to
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected table_name to be a string")
    if not isinstance(column_name, str):
        raise TypeError("Expected column name to be a string")
    if not isinstance(row_id, int):
        raise TypeError("Expected row_id to be a string")

    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[column_name]

    stmt = sqlalchemy.update(table).where(id_column == row_id).values({target_column: value})

    engine = tool.db_engine
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
