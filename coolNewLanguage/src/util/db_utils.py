# def create_table_from_csv(
#         table_name: UserInputComponent | str,
#         csv_file: FileUploadComponent,
#         has_header: bool = True,
#         overwrite_existing: bool = True,
#         get_user_approvals: bool = False
# ) -> sqlalchemy.Table:
#     """
#     Create a table in the database of the tool, using the csv file as the source for the data
#     :param table_name: The name to use for the table being inserted
#     :param csv_file: The csv file to use as the data source
#     :param has_header: Whether the passed csv file has a header or not
#     :param overwrite_existing: Whether to overwrite an existing table with the same name
#     :param get_user_approvals: Whether to get user approvals before committing data
#     :return: The created table
#     """
#     if not isinstance(table_name, UserInputComponent) and not isinstance(table_name, str):
#         raise TypeError("Expected a User Input or a string for table name")
#     if isinstance(table_name, UserInputComponent) and table_name.value is None:
#         raise ValueError("Expected User Input to have a value for table name")
#     if isinstance(table_name, UserInputComponent) and not isinstance(table_name.value, str):
#         raise ValueError("Expected User Input value to be a string for table name")
#
#     if isinstance(table_name, UserInputComponent):
#         table_name = table_name.value
#
#     if table_name.startswith('__'):
#         raise ValueError("User created tables cannot begin with '__'")
#
#     # Check whether a table with the passed name already exists
#     tool: toolModule.Tool = process.running_tool
#     metadata = tool.db_metadata_obj
#     if table_name in tool.get_table_names():
#         table = tool.get_table_from_table_name(table_name)
#         if not overwrite_existing:
#             raise ValueError("A table with this name already exists")
#         else:
#             # drop existing table
#             table.drop(bind=tool.db_engine)
#             metadata.remove(table)
#
#     if not isinstance(csv_file, FileUploadComponent):
#         raise TypeError("Expected a File Upload for csv file")
#     if csv_file.value is None:
#         raise ValueError("Expected File Upload to have a value for csv file")
#     if not isinstance(csv_file.value, Path):
#         raise ValueError("Expected File Upload value to be a Path to a file")
#     if not isinstance(has_header, bool):
#         raise TypeError("Expected a bool for has_header")
#
#     # create table
#     metadata_obj: sqlalchemy.MetaData = tool.db_metadata_obj
#     with open(csv_file.value) as f:
#         table = sqlalchemy_table_from_csv_file(table_name, f, metadata_obj, has_header)
#
#     # If get_user_approvals is on, cache the table as an ApprovalResult
#     if get_user_approvals:
#         from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
#         # Convert csv file to a list of lists
#         with open(csv_file.value) as f:
#             data = [row for row in csv.reader(f)]
#         approve_result = TableApproveResult(data, table_name, table)
#         process.approve_results.append(approve_result)
#         return table
#
#     metadata_obj.create_all(tool.db_engine)
#     # insert data
#     with open(csv_file.value) as f:
#         insert_stmt = sqlalchemy_insert_into_table_from_csv_file(table, f, has_header)
#     with tool.db_engine.connect() as conn:
#         conn.execute(insert_stmt)
#         conn.commit()
#
#     return table
#
#
# def create_table_from_lists(
#         table_name: str,
#         data: list[list],
#         return_existing_table: bool = False,
#         overwrite_existing_table: bool = True,
#         get_user_approvals: bool = False
# ) -> sqlalchemy.Table:
#     """
#     Create and commit a table in the database of the currently running tool, populating it with data passed in as a list
#     of lists. Assumes the first row contains the column names for the table.
#
#     :param table_name: The name to give the table
#     :param data: The data to use to populate the created table, passed as a list of lists
#     :param return_existing_table: A boolean describing whether to run if an existing table with the same name already
#         exists. If such a table exists, return that table.
#     :param overwrite_existing_table: A boolean describing whether to overwrite if an existing table with the same name
#         already exists.
#     :param get_user_approvals: A boolean describing whether to get user approvals for the table before saving it to the
#         database.
#     :return: The created sqlalchemy Table
#     """
#     # if not running process, exit
#     if not process.handling_post:
#         return
#
#     if not isinstance(table_name, str):
#         raise TypeError("Expected table_name to be a string")
#
#     if table_name.startswith('__'):
#         raise ValueError("User created tables cannot begin with '__'")
#
#     # Check whether a table with the passed name already exists
#     tool: toolModule.Tool = process.running_tool
#     metadata = tool.db_metadata_obj
#     if table_name in tool.get_table_names():
#         table = tool.get_table_from_table_name(table_name)
#         if return_existing_table:
#             return table
#         if not overwrite_existing_table:
#             raise ValueError("A table with this name already exists")
#         else:
#             # drop existing table
#             table.drop(bind=tool.db_engine)
#             metadata.remove(table)
#
#     if not isinstance(data, list):
#         raise TypeError("Expected data to be a list")
#     if not all([isinstance(row, list) for row in data]):
#         raise TypeError("Expected each element of data to be a list")
#     # Check that the first row is all strings, as it should be column names
#     if not all([isinstance(column_name, str) for column_name in data[0]]):
#         raise TypeError("Expected all the elements of the first row to be a string")
#
#     # Validate the shape of data
#     if not all([len(row) == len(data[0]) for row in data]):
#         raise ValueError("Expected all rows of data to have the same length")
#
#     # Create the table
#     cols = [sqlalchemy.Column(DB_INTERNAL_COLUMN_ID_NAME, sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)]
#     col_names = data[0]
#     for i, col_name in enumerate(col_names):
#         if col_name == '':
#             cols.append(sqlalchemy.Column(f'Col {i}', sqlalchemy.String))
#         else:
#             cols.append(sqlalchemy.Column(col_name, sqlalchemy.String))
#     table = sqlalchemy.Table(table_name, metadata, *cols, extend_existing=True)
#
#     # If get_user_approvals is on, cache the table as an ApprovalResult
#     if get_user_approvals:
#         from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
#         approve_result = TableApproveResult(data, table_name, table)
#         process.approve_results.append(approve_result)
#         return table
#
#     # Commit created table
#     metadata.create_all(tool.db_engine)
#
#     # Construct insert statement
#     records = []
#     for row in data[1:]:
#         record = {col_name: row[i] for i, col_name in enumerate(col_names)}
#         records.append(record)
#     insert_stmt = sqlalchemy.insert(table).values(records)
#
#     # Commit insert statement
#     with tool.db_engine.connect() as conn:
#         conn.execute(insert_stmt)
#         conn.commit()
#
#     return table

# def iterate_over_columns(tool: toolModule.Tool, table: sqlalchemy.Table, column_names: list[str]) -> Iterator[Tuple[int, Any]]:
#     """
#     Iterate over the table with the passed columns, yielding the values of the passed columns for each row
#     :param tool: The tool containing the associated table
#     :param table: The sqlalchemy Table containing the columns of interest
#     :param column_names: The names of the columns to iterate over
#     :return: Yields a tuple of form (row_id, values, ...)
#     """
#     if not isinstance(tool, toolModule.Tool):
#         raise TypeError("Expected tool to be a Tool")
#     if not isinstance(table, sqlalchemy.Table):
#         raise TypeError("Expected table to be a sqlalchemy Table")
#     if not isinstance(column_names, list) or not all(isinstance(col_name, str) for col_name in column_names):
#         raise TypeError("Expected column_names to be a list of strings")
#
#     engine = tool.db_engine
#     id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
#     target_columns = [table.c[column_name] for column_name in column_names]
#
#     query = sqlalchemy.select(id_column, *target_columns)
#     with engine.connect() as conn:
#         query_result = conn.execute(query)
#     yield from query_result
#
#
# def update_cell(tool: toolModule.Tool, table: sqlalchemy.Table, column_name: str, row_id: int, value: Any):
#     """
#     Update the given cell, identified by the table_name, column_name and row_id, to the passed value
#     :param tool: The Tool which owns the table with the cell to be updated
#     :param table: The table with the cell to be updated
#     :param column_name: The name of the column containing the cell to be updated
#     :param row_id: The row containing the cell to be updated
#     :param value: The value to update the cell to
#     :return:
#     """
#     if not isinstance(tool, toolModule.Tool):
#         raise TypeError("Expected tool to be a Tool")
#     if not isinstance(table, sqlalchemy.Table):
#         raise TypeError("Expected table_name to be a string")
#     if not isinstance(column_name, str):
#         raise TypeError("Expected column name to be a string")
#     if not isinstance(row_id, int):
#         raise TypeError("Expected row_id to be an int")
#
#     id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
#     target_column = table.c[column_name]
#
#     stmt = sqlalchemy.update(table).where(id_column == row_id).values({target_column: value})
#
#     engine = tool.db_engine
#     with engine.connect() as conn:
#         conn.execute(stmt)
#         conn.commit()
#
#
# def get_cell_value(tool: toolModule.Tool, table: sqlalchemy.Table, column_name: str, row_id: int) -> str:
#     """
#     Get the value of the given cell, identified by the table_name, column_name and row_id
#     :param tool: The Tool which owns the table with the cell to be read
#     :param table: The table with the cell to be read
#     :param column_name: The name of the column containing the cell to be read
#     :param row_id: The row containing the cell to be read
#     :return: The value of the cell, expected to be a string (for now)
#     """
#     if not isinstance(tool, toolModule.Tool):
#         raise TypeError("Expected tool to be a Tool")
#     if not isinstance(table, sqlalchemy.Table):
#         raise TypeError("Expected table_name to be a string")
#     if not isinstance(column_name, str):
#         raise TypeError("Expected column name to be a string")
#     if not isinstance(row_id, int):
#         raise TypeError("Expected row_id to be a string")
#
#     id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
#     target_column = table.c[column_name]
#
#     stmt = sqlalchemy.select(target_column).where(id_column == row_id)
#     with tool.db_engine.connect() as conn:
#         return conn.execute(stmt)[0][0]
#
#
# def update_column(tool: toolModule.Tool, table: sqlalchemy.Table, col_name: str, row_id_val_pairs: List[Tuple[int, Any]]):
#     """
#     Update the column of the given table, with each value to update identified by its row id
#     :param tool: The Tool which owns the table with the column to be updated
#     :param table: The table with the column to be updated
#     :param col_name: The name of the column to be updated
#     :param row_id_val_pairs: A list of tuples, of form (row_id, val), where we update table[row_id][column_name] to be
#     val
#     :return:
#     """
#
#     id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
#     target_column = table.c[col_name]
#
#     stmt = sqlalchemy.update(table)\
#         .where(id_column == sqlalchemy.bindparam("row_id"))\
#         .values({target_column: sqlalchemy.bindparam("val")})
#
#     with tool.db_engine.connect() as conn:
#         conn.execute(
#             stmt,
#             [{"row_id": row_id, "val": val} for row_id, val in row_id_val_pairs]
#         )
#         conn.commit()
#
#
# def get_rows_of_table(tool: toolModule.Tool, table: sqlalchemy.Table) -> Sequence[sqlalchemy.Row]:
#     """
#     Get the rows of this table using a select statement
#     :param tool: The Tool which owns the table from which to get the rows
#     :param table: The table to get the rows from
#     :return:
#     """
#     if not isinstance(tool, toolModule.Tool):
#         raise TypeError("Expected tool to be a Tool")
#     if not isinstance(table, sqlalchemy.Table):
#         raise TypeError("Expected table_name to be a string")
#
#     stmt = sqlalchemy.select(table)
#     with tool.db_engine.connect() as conn:
#         results = conn.execute(stmt)
#
#     return results.all()
#
#
# def get_row(tool: toolModule.Tool, table_name: str, row_id: int) -> 'Row':
#     """
#     Get the row of the passed table with the passed row id
#     :param tool: The tool which owns the table
#     :param table_name: The name of the table to get the row from
#     :param row_id: The id of the target row
#     :return: A CNL Row corresponding to the desired row
#     """
#     from coolNewLanguage.src.row import Row
#
#     if not isinstance(tool, toolModule.Tool):
#         raise TypeError("Expected tool to be a Tool")
#     if not isinstance(table_name, str):
#         raise TypeError("Expected table_name to be a string")
#     if not isinstance(row_id, int):
#         raise TypeError("Expected row_id to be an int")
#
#     table = tool.get_table_from_table_name(table_name)
#
#     stmt = sqlalchemy.select(table).where(table.c[DB_INTERNAL_COLUMN_ID_NAME] == row_id)
#     with tool.db_engine.connect() as conn:
#         sqlalchemy_row = conn.execute(stmt).first()
#
#     return Row(table, sqlalchemy_row)
#
# # TODO: Put all the linking stuff in one file?
