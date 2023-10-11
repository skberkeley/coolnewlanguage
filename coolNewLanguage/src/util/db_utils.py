import datetime
import enum
from pathlib import Path

import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from typing import List, Tuple, Any, Iterator, Sequence, Optional

from coolNewLanguage.src.row import Row
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
        table_name: UserInputComponent | str,
        csv_file: FileUploadComponent,
        has_header: bool = True
) -> sqlalchemy.Table:
    """
    Create a table in the database of the tool, using the csv file as the source for the data
    :param table_name: The name to use for the table being inserted
    :param csv_file: The csv file to use as the data source
    :param has_header: Whether the passed csv file has a header or not
    :return: The created table
    """
    if not isinstance(table_name, UserInputComponent) and not isinstance(table_name, str):
        raise TypeError("Expected a User Input or a string for table name")
    if isinstance(table_name, UserInputComponent) and table_name.value is None:
        raise ValueError("Expected User Input to have a value for table name")
    if isinstance(table_name, UserInputComponent) and not isinstance(table_name.value, str):
        raise ValueError("Expected User Input value to be a string for table name")

    if isinstance(table_name, UserInputComponent):
        table_name = table_name.value

    if table_name.startswith('__'):
        raise ValueError("User created tables cannot begin with '__'")

    # Check whether a table with the passed name already exists
    tool = process.running_tool
    if table_name in get_table_names_from_tool(tool, True):
        raise ValueError("A table with this name already exists")

    if not isinstance(csv_file, FileUploadComponent):
        raise TypeError("Expected a File Upload for csv file")
    if csv_file.value is None:
        raise ValueError("Expected File Upload to have a value for csv file")
    if not isinstance(csv_file.value, Path):
        raise ValueError("Expected File Upload value to be a Path to a file")
    if not isinstance(has_header, bool):
        raise TypeError("Expected a bool for has_header")

    # create table
    metadata_obj: sqlalchemy.MetaData = tool.db_metadata_obj
    with open(csv_file.value) as f:
        table = sqlalchemy_table_from_csv_file(table_name, f, metadata_obj, has_header)
    metadata_obj.create_all(tool.db_engine)
    # insert data
    with open(csv_file.value) as f:
        insert_stmt = sqlalchemy_insert_into_table_from_csv_file(table, f, has_header)
    with tool.db_engine.connect() as conn:
        conn.execute(insert_stmt)
        conn.commit()

    return table


def create_table_from_lists(
        table_name: str,
        data: list[list],
        return_existing_table: bool = True,
        overwrite_existing_table: bool = False,
        get_user_approvals: bool = False
) -> sqlalchemy.Table:
    """
    Create and commit a table in the database of the currently running tool, populating it with data passed in as a list
    of lists. Assumes the first row contains the column names for the table.

    :param table_name: The name to give the table
    :param data: The data to use to populate the created table, passed as a list of lists
    :param return_existing_table: A boolean describing whether to run if an existing table with the same name already
        exists. If such a table exists, return that table.
    :param overwrite_existing_table: A boolean describing whether to overwrite if an existing table with the same name
        already exists.
    :param get_user_approvals: A boolean describing whether to get user approvals for the table before saving it to the
        database.
    :return: The created sqlalchemy Table
    """
    # if not running process, exit
    if not process.handling_post:
        return

    if not isinstance(table_name, str):
        raise TypeError("Expected table_name to be a string")

    if table_name.startswith('__'):
        raise ValueError("User created tables cannot begin with '__'")

    # Check whether a table with the passed name already exists
    tool: Tool = process.running_tool
    metadata = tool.db_metadata_obj
    if table_name in get_table_names_from_tool(tool, True):
        table = get_table_from_table_name(tool, table_name)
        if return_existing_table:
            return table
        if not overwrite_existing_table:
            raise ValueError("A table with this name already exists")
        else:
            # drop existing table
            table.drop(bind=tool.db_engine)
            metadata.remove(table)

    if not isinstance(data, list):
        raise TypeError("Expected data to be a list")
    if not all([isinstance(row, list) for row in data]):
        raise TypeError("Expected each element of data to be a list")
    # Check that the first row is all strings, as it should be column names
    if not all([isinstance(column_name, str) for column_name in data[0]]):
        raise TypeError("Expected all the elements of the first row to be a string")

    # Validate the shape of data
    if not all([len(row) == len(data[0]) for row in data]):
        raise ValueError("Expected all rows of data to have the same length")

    # Create the table
    cols = [sqlalchemy.Column(DB_INTERNAL_COLUMN_ID_NAME, sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)]
    col_names = data[0]
    for i, col_name in enumerate(col_names):
        if col_name == '':
            cols.append(sqlalchemy.Column(f'Col {i}', sqlalchemy.String))
        else:
            cols.append(sqlalchemy.Column(col_name, sqlalchemy.String))
    table = sqlalchemy.Table(table_name, metadata, *cols, extend_existing=True)

    # If get_user_approvals is on, cache the table as an ApprovalResult
    if get_user_approvals:
        from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
        approve_result = TableApproveResult(data, table_name, table)
        process.approve_results.append(approve_result)
        return table

    # Commit created table
    metadata.create_all(tool.db_engine)

    # Construct insert statement
    records = []
    for row in data[1:]:
        record = {col_name: row[i] for i, col_name in enumerate(col_names)}
        records.append(record)
    insert_stmt = sqlalchemy.insert(table).values(records)

    # Commit insert statement
    with tool.db_engine.connect() as conn:
        conn.execute(insert_stmt)
        conn.commit()

    return table


def create_table_if_not_exists(tool: Tool, table_name: str, fields: dict[str, 'Field']) -> sqlalchemy.Table:
    """
    Create a table in the backend of the passed Tool if one with the passed name does not already exist. Uses the passed
    fields dictionary to figure out what columns this table should have. Returns the created table, or the table that
    already exists.
    :param tool: The tool whose backend within which the table should be created.
    :param table_name: The name to give the table.
    :param fields: A dictionary from field_name to Field instances, used to determine the columns to give the table.
    :return:
    """
    from coolNewLanguage.src.cnl_type.field import Field

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


def get_table_names_from_tool(tool: Tool, only_user_tables: bool = True) -> List[str]:
    """
    Get the names of the database tables associated with the passed table
    :param tool: The Tool from which to get associated table names
    :param only_user_tables: Whether to fetch only user-created tables
    :return: A list of table names
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected a Tool for tool")

    engine = tool.db_engine
    insp = sqlalchemy.inspect(engine)
    all_table_names = insp.get_table_names()

    if only_user_tables:
        return list(filter(lambda table_name: not table_name.startswith('__'), all_table_names))
    return all_table_names


def get_column_names_from_table_name(tool: Tool, table_name: str, only_user_columns: bool = True) -> List[str]:
    """
    Get the column names of the passed table
    :param tool: The Tool with which the table is associated
    :param table_name: The name of the table from which to get the column names
    :param only_user_columns: Whether the column names should be filtered to include only user columns
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

    if only_user_columns:
        return filter_to_user_columns(columns)
    return columns


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


def get_row(tool: Tool, table_name: str, row_id: int) -> Row:
    """
    Get the row of the passed table with the passed row id
    :param tool: The tool which owns the table
    :param table_name: The name of the table to get the row from
    :param row_id: The id of the target row
    :return: A CNL Row corresponding to the desired row
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(table_name, str):
        raise TypeError("Expected table_name to be a string")
    if not isinstance(row_id, int):
        raise TypeError("Expected row_id to be an int")

    table = get_table_from_table_name(tool, table_name)

    stmt = sqlalchemy.select(table).where(table.c[DB_INTERNAL_COLUMN_ID_NAME] == row_id)
    with tool.db_engine.connect() as conn:
        sqlalchemy_row = conn.execute(stmt).first()

    return Row(table, sqlalchemy_row)

# TODO: Put all the linking stuff in one file?


def db_awaken(tool: Tool):
    """
    Creates/gets necessary tables in backend, and is called when the tool is instantiated
    Creates the LINKS_META table, which encodes the existing Link metatypes, and the LINKS table, which acts as a
    registry of the individual links themselves.
    :param tool: The Tool for which the db is being awakened.
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")

    if get_table_from_table_name(tool, consts.LINKS_METATYPES_TABLE_NAME) is None:
        cols = [
            sqlalchemy.Column(
                consts.LINKS_METATYPES_LINK_META_ID,
                sqlalchemy.Integer,
                sqlalchemy.Identity(),
                primary_key=True),
            sqlalchemy.Column(consts.LINKS_METATYPES_LINK_META_NAME, sqlalchemy.String, nullable=False, unique=True)
        ]
        links_metatypes_table = sqlalchemy.Table(consts.LINKS_METATYPES_TABLE_NAME, tool.db_metadata_obj, *cols)
        links_metatypes_table.create(tool.db_engine)

    if get_table_from_table_name(tool, consts.LINKS_REGISTRY_TABLE_NAME) is None:
        cols = [
            sqlalchemy.Column(
                consts.LINKS_REGISTRY_LINK_ID,
                sqlalchemy.Integer,
                sqlalchemy.Identity(),
                primary_key=True),
            sqlalchemy.Column(consts.LINKS_REGISTRY_LINK_META_ID, sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(consts.LINKS_REGISTRY_SRC_TABLE_NAME, sqlalchemy.String, nullable=False),
            sqlalchemy.Column(consts.LINKS_REGISTRY_SRC_ROW_ID, sqlalchemy.Integer, nullable=False),
            sqlalchemy.Column(consts.LINKS_REGISTRY_DST_TABLE_NAME, sqlalchemy.String, nullable=False),
            sqlalchemy.Column(consts.LINKS_REGISTRY_DST_ROW_ID, sqlalchemy.Integer, nullable=False)
        ]
        links_registry_table = sqlalchemy.Table(consts.LINKS_REGISTRY_TABLE_NAME, tool.db_metadata_obj, *cols)
        links_registry_table.create(tool.db_engine)
