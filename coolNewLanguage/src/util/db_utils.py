from pathlib import Path

import sqlalchemy

from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.sql_alch_csv_utils import *
from coolNewLanguage.src.component.table_selector import *
from typing import List


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

    table.engine = tool.db_engine

    return table


def get_tables(tool: Tool) -> List[str]:
    engine = tool.db_engine
    insp = sqlalchemy.inspect(engine)
    return insp.get_table_names()

def get_table_columns(tool: Tool, table: str) -> List[str]:
    engine = tool.db_engine
    insp = sqlalchemy.inspect(engine)
    columns = [str(col["name"]) for col in insp.get_columns(table_name=table)]
    return filter_to_user_columns(columns)

def get_table(tool:Tool, table_name:str) -> sqlalchemy.Table:
    engine = tool.db_engine
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine)
    return sqlalchemy.Table(table_name, metadata)

def iterate_column(tool: Tool, table_name:str, column_name:str) -> Tuple[int, any]:
    engine = tool.db_engine
    table = get_table(tool, table_name)
    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[column_name]

    query = sqlalchemy.select(id_column, target_column)
    with engine.connect() as conn:
        yield from conn.execute(query)
        # results = conn.execute(query).fetchall()
        # print(results)

def assign_column_value(tool:Tool, table_name:str, column_name:str, column_id:int, value):
    engine = tool.db_engine
    table = get_table(tool, table_name)
    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[column_name]

    stmt = sqlalchemy.update(table).where(id_column == column_id).values({
        target_column : value
    })

    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
        print("updated", result.rowcount)
