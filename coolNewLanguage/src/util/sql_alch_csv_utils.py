import csv
import io

import sqlalchemy


def sqlalchemy_table_from_csv_file(table_name: str, csv_file: io.IOBase, sqlalch_metadata: sqlalchemy.MetaData, has_header: bool = True) -> sqlalchemy.Table:
    """
    Create a SQLAlchemy Table object from the given csv file. Note that this function only determines the schema from
    the csv, rather than actually inserting data into some database. If a table with the passed name already exists,
    that Table object will be returned, aligning with SQLAlchemy behavior.
    :param table_name: Name to give table
    :param csv_file: The CSV file to read from
    :param sqlalch_metadata: The SQLAlchemy MetaData object to use to instantiate the table
    :param has_header: Whether the passed csv_file has a header row to read column names from
    :return: A SQLAlchemy Table object
    """
    if not isinstance(table_name, str):
        raise TypeError("Expected a string for table_name")
    if not isinstance(csv_file, io.IOBase):
        raise TypeError("Expected a readable object for csv_file")
    if not isinstance(sqlalch_metadata, sqlalchemy.MetaData):
        raise TypeError("Expected a SQLAlchemy MetaData object for sqlalch_metadata")
    if not isinstance(has_header, bool):
        raise TypeError("Expected a bool for has_header")

    dialect = csv.Sniffer().sniff(csv_file.read(1024))
    csv_file.seek(0)
    reader = csv.reader(csv_file, dialect)

    header = reader.__next__()
    if has_header:
        cols = []
        for i, col_name in enumerate(header):
            if col_name == '':
                cols.append(sqlalchemy.Column(f'Col {i}', sqlalchemy.String))
            else:
                cols.append(sqlalchemy.Column(col_name, sqlalchemy.String))
    else:
        cols = [sqlalchemy.Column(f'Col {i}', sqlalchemy.String) for i in range(len(header))]

    return sqlalchemy.Table(table_name, sqlalch_metadata, *cols)


def sqlalchemy_insert_into_table_from_csv_file(table: sqlalchemy.Table, csv_file: io.IOBase, has_header: bool = True) -> sqlalchemy.sql.expression.Insert:
    """
    Constructs a SQLAlchemy insert object which inserts into the passed table from the data contained in the CSV file
    Assumes the table already has the correct schema to accomodate the csv file's data
    :param table: The SQLAlchemy table to insert into
    :param csv_file: The CSV file containing the data to insert
    :param has_header: Whether the csv file has a header to be ignored when inserting data
    :return: The SQLAlchemy Insert object representing the statement which inserts the csv file's data into the table
    """
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected a SQLAlchemy Table for table")
    if not isinstance(csv_file, io.IOBase):
        raise TypeError("Expected a readable object for csv_file")
    if not isinstance(has_header, bool):
        raise TypeError("Expected a bool for has_header")

    dialect = csv.Sniffer().sniff(csv_file.read(1024))
    csv_file.seek(0)
    reader = csv.reader(csv_file, dialect)

    # Construct records
    records = []
    # skip the header if needed
    if has_header:
        reader.__next__()
    # for each row in the csv, construct the appropriate record
    col_names = table.columns.keys()
    for row in reader:
        if len(row) < len(col_names):
            record = {col_names[i]: elem for i, elem in enumerate(row)}
        else:
            record = {col_name: row[i] for i, col_name in enumerate(col_names)}
        records.append(record)
    # Construct insert statement
    return sqlalchemy.insert(table).values(records)
