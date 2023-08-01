import datetime
import enum
from pathlib import Path

import sqlalchemy

from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from typing import List, Tuple, Any, Iterator, Sequence, Optional

from coolNewLanguage.src.stage import process
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.sql_alch_csv_utils import sqlalchemy_table_from_csv_file, \
    sqlalchemy_insert_into_table_from_csv_file, filter_to_user_columns, DB_INTERNAL_COLUMN_ID_NAME


PYTHON_TYPE_TO_SQLALCHEMY_TYPE: dict[type, type[sqlalchemy.types.TypeEngine]] = {
    bool: sqlalchemy.types.Boolean,
    datetime.date: sqlalchemy.types.Date,
    datetime.datetime: sqlalchemy.types.DateTime,
    enum.Enum: sqlalchemy.types.Enum,
    float: sqlalchemy.types.Float,
    int: sqlalchemy.types.Integer,
    datetime.timedelta: sqlalchemy.types.Interval,
    str: sqlalchemy.types.String,
    datetime.time: sqlalchemy.types.Time
}


def create_table_from_csv(
        table_name: UserInputComponent,
        csv_file: FileUploadComponent,
        has_header: bool = True
) -> sqlalchemy.Table:
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


def create_table_if_not_exists(tool: Tool, table_name: str, fields: dict[str, Field]) -> sqlalchemy.Table:
    """
    Create a table in the backend of the passed Tool if one with the passed name does not already exist. Uses the passed
    fields dictionary to figure out what columns this table should have. Returns the created table, or the table that
    already exists.
    :param tool: The tool whose backend within which the table should be created.
    :param table_name: The name to give the table.
    :param fields: A dictionary from field_name to Field instances, used to determine the columns to give the table.
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(table_name, str):
        raise TypeError("Expected table_name to be a string")
    if not isinstance(fields, dict):
        raise TypeError("Expected fields to be a dictionary")
    if not all([isinstance(key, str) and isinstance(value, Field) for key, value in fields.items()]):
        raise TypeError("Expected fields to map from strings to Fields")

    table = get_table_from_table_name(tool, table_name)
    if table is not None:
        return table

    metadata_obj = tool.db_metadata_obj
    cols = [
        sqlalchemy.Column(DB_INTERNAL_COLUMN_ID_NAME, sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)
    ]

    name: str
    field: Field
    for name, field in fields.items():
        sql_type = PYTHON_TYPE_TO_SQLALCHEMY_TYPE[field.data_type]
        cols.append(sqlalchemy.Column(name, sql_type, nullable=field.optional))

    table = sqlalchemy.Table(table_name, metadata_obj, *cols)
    table.create(tool.db_engine)
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


def get_table_from_table_name(tool: Tool, table_name: str) -> Optional[sqlalchemy.Table]:
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
        return None
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
        raise TypeError("Expected row_id to be an int")

    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[column_name]

    stmt = sqlalchemy.update(table).where(id_column == row_id).values({target_column: value})

    engine = tool.db_engine
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def get_cell_value(tool: Tool, table: sqlalchemy.Table, column_name: str, row_id: int) -> str:
    """
    Get the value of the given cell, identified by the table_name, column_name and row_id
    :param tool: The Tool which owns the table with the cell to be read
    :param table: The table with the cell to be read
    :param column_name: The name of the column containing the cell to be read
    :param row_id: The row containing the cell to be read
    :return: The value of the cell, expected to be a string (for now)
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

    stmt = sqlalchemy.select(target_column).where(id_column == row_id)
    with tool.db_engine.connect() as conn:
        return conn.execute(stmt)[0][0]


def update_column(tool: Tool, table: sqlalchemy.Table, col_name: str, row_id_val_pairs: List[Tuple[int, Any]]):
    """
    Update the column of the given table, with each value to update identified by its row id
    :param tool: The Tool which owns the table with the column to be updated
    :param table: The table with the column to be updated
    :param col_name: The name of the column to be updated
    :param row_id_val_pairs: A list of tuples, of form (row_id, val), where we update table[row_id][column_name] to be
    val
    :return:
    """

    id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
    target_column = table.c[col_name]

    stmt = sqlalchemy.update(table)\
        .where(id_column == sqlalchemy.bindparam("row_id"))\
        .values({target_column: sqlalchemy.bindparam("val")})

    with tool.db_engine.connect() as conn:
        conn.execute(
            stmt,
            [{"row_id": row_id, "val": val} for row_id, val in row_id_val_pairs]
        )
        conn.commit()


def get_rows_of_table(tool: Tool, table: sqlalchemy.Table) -> Sequence[sqlalchemy.Row]:
    """
    Get the rows of this table using a select statement
    :param tool: The Tool which owns the table from which to get the rows
    :param table: The table to get the rows from
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected table_name to be a string")

    stmt = sqlalchemy.select(table)
    with tool.db_engine.connect() as conn:
        results = conn.execute(stmt)

    return results.all()

# TODO: Consts should live in consts.py
# TODO: Better names for these consts?
LINKS_META = "__hls_links_meta"
LINKS_META_LINK_META_ID = "link_meta_id"
LINKS_META_TABLE_NAME = "table_name"
LINKS_META_FIELD_NAME = "field_name"

LINKS = "__hls_links"
LINKS_META_ID = "link_meta_id"
LINKS_SRC_ROW_ID = "src_row_id"
LINKS_DST_TABLE_NAME = "dst_table_name"
LINKS_DST_ROW_ID = "dst_row_id"
# TODO: Put all the linking stuff in one file?
def db_awaken(tool: Tool):
    # TODO: Flesh out docstring
    """
    Creates/gets necessary tables in backend when Tool is instantiated
    :param tool:
    :return:
    """
    # TODO: check type
    metadata_obj = tool.db_metadata_obj
    
    links_meta = get_table_from_table_name(tool, LINKS_META)
    if links_meta is None:
        links_meta = sqlalchemy.Table(LINKS_META, metadata_obj, 
            sqlalchemy.Column(LINKS_META_LINK_META_ID, sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True),
            sqlalchemy.Column(LINKS_META_TABLE_NAME, sqlalchemy.String, nullable=False),
            sqlalchemy.Column(LINKS_META_FIELD_NAME, sqlalchemy.String, nullable=False),
        )
        links_meta.create(tool.db_engine)
    
    links = get_table_from_table_name(tool, LINKS)
    if links is None:
        links = sqlalchemy.Table(LINKS, metadata_obj, 
            sqlalchemy.Column("id", sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True),
            sqlalchemy.Column(LINKS_META_ID, sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(LINKS_SRC_ROW_ID, sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(LINKS_DST_TABLE_NAME, sqlalchemy.String, nullable=False),
            sqlalchemy.Column(LINKS_DST_ROW_ID, sqlalchemy.Integer, nullable=False),
        )
        links.create(tool.db_engine)

def get_link_registration_id(tool:Tool, table_name:str, field:str) -> Optional[int]:
    # TODO: rename field parameter, since it implies that it should be of type Field
    # TODO: check types
    links_meta = get_table_from_table_name(tool, LINKS_META)
    stmt = sqlalchemy.select(links_meta.c[LINKS_META_LINK_META_ID])\
        .where(links_meta.c[LINKS_META_TABLE_NAME] == table_name)\
        .where(links_meta.c[LINKS_META_FIELD_NAME] == field)

    with tool.db_engine.connect() as conn:
        # TODO: Debug this and see why we need to index, adding comments explaining why
        result = conn.execute(stmt).first()
        print(result)
        if result:
            return result[0]
        else:
            return None


def link_register(tool:Tool, table_name:str, field:str) -> Optional[int]:
    # TODO: do type checks
    existing = get_link_registration_id(tool, table_name, field)
    if existing is not None:
        return existing
    
    table = get_table_from_table_name(tool, LINKS_META)
    insert_stmt = sqlalchemy.insert(table).values({
        LINKS_META_TABLE_NAME: table_name,
        LINKS_META_FIELD_NAME: field
    })
    with tool.db_engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()
    
    return result.inserted_primary_key

def link_create(tool: Tool, link_id:int, src_row_id:int, dst_table:str, dst_row_id:int):
    # TODO: type checks
    # TODO: Check to see if the link exists already
    table = get_table_from_table_name(tool, LINKS)
    insert_stmt = sqlalchemy.insert(table).values({
        LINKS_META_ID: link_id,
        LINKS_SRC_ROW_ID: src_row_id,
        LINKS_DST_TABLE_NAME: dst_table,
        LINKS_DST_ROW_ID : dst_row_id
    })
    with tool.db_engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()
        return result.inserted_primary_key