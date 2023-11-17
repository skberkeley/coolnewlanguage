from typing import Optional

import jinja2
import sqlalchemy.sql.expression

from coolNewLanguage.src import consts
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util import db_utils


def template_from_select_statement(
        stmt: sqlalchemy.sql.expression.Select,
        template: jinja2.Template,
        table_name: str = "",
        num_rows: Optional[int] = None
) -> str:
    """
    Construct an HTML table containing the results of the passed Select statement
    :param stmt: The select statement to run and render the results of
    :param template: The template to use to render the results
    :param table_name: The name of the table the select statement is selecting from, to be included as part of the
    template
    :param num_rows: The number of rows to include in the template. If None, all rows are included
    :return: A string containing an HTML table containing the results
    """
    if not isinstance(stmt, sqlalchemy.sql.expression.Select):
        raise TypeError("Expected stmt to be a sqlalchemy Select")
    if not isinstance(table_name, str):
        raise TypeError("Expected table_name to be a string")
    if num_rows is not None and not isinstance(num_rows, int):
        raise TypeError("Expected num_rows to be an int or None")

    col_names = stmt.selected_columns.keys()

    # if a limit is specified, add it to the select statement
    if num_rows is not None:
        stmt = stmt.limit(num_rows)

    # table contents
    with process.running_tool.db_engine.connect() as conn:
        rows = [row._mapping for row in conn.execute(stmt)]

    # render and return it
    return template.render(col_names=col_names, rows=rows, table_name=table_name)

def html_of_table(
        table: sqlalchemy.Table,
        template: jinja2.Template,
        num_rows: Optional[int] = None,
        include_table_name: bool = True
) -> str:
    """
    Construct an HTML snippet of a sqlalchemy Table
    If the table doesn't exist in the underlying db, returns an emtpy string
    :param table: The table to construct the template for
    :param template: The template to use to render the table
    :param num_rows: The number of rows to include in the template. If None, all rows are included
    :param include_table_name: Whether to include the table name in the template
    :return: A string containing the HTML table the table with the table's data
    """
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected table to be a sqlalchemy Table")
    if num_rows is not None and not isinstance(num_rows, int):
        raise TypeError("Expected num_rows to be an int or None")

    # Check to see if the table exists in the db, since it may be newly created and all its rows may have been rejected
    if table.name not in process.running_tool.db_metadata_obj.tables:
        return ""

    stmt = sqlalchemy.select(table)

    return template_from_select_statement(
        stmt,
        template,
        table_name=table.name if include_table_name else "",
        num_rows=num_rows
    )



def html_of_row_list(rows: list[Row]) -> str:
    """
    Construct an HTML snippet of some rows, all assumed to be from the same table
    :param rows: The rows from which to get the data for
    :return: A string containing an HTML table with data from the rows
    """
    if not isinstance(rows, list):
        raise TypeError("Expected rows to be a list")
    if not all([isinstance(r, Row) for r in rows]):
        raise TypeError("Expected each element of rows to be a Row")

    col_names = rows[0].keys()
    # construct rows for use in Jinja template
    # each row should be dict[col_name --> string[val]
    # Note: row's __getitem__ returns a Cell
    jinja_rows = []
    for row in rows:
        jinja_row = {}
        for col in col_names:
            jinja_row[col] = str(row[col].get_val())
        jinja_rows.append(jinja_row)

    # Get Jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.TABLE_RESULT_TEMPLATE_FILENAME
    )
    # Render and return template
    return template.render(col_names=col_names, rows=jinja_rows)


def html_of_link(link: Link) -> str:
    """
    Construct an HTML snippet of a link
    :param link: The link to render
    :return: A string containing an HTML table with the data from the link
    """
    if not isinstance(link, Link):
        raise TypeError("Expected link to be a Link")

    # Get src row
    src_row = db_utils.get_row(process.running_tool, link.src_table_name, link.src_row_id)
    src_row_html = html_of_row_list([src_row])

    # Get dst row
    dst_row = db_utils.get_row(process.running_tool, link.dst_table_name, link.dst_row_id)
    dst_row_html = html_of_row_list([dst_row])

    # Get Jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.LINK_RESULT_TEMPLATE_FILENAME
    )
    # Render and return template
    return template.render(src_row_html=src_row_html, dst_row_html=dst_row_html)

