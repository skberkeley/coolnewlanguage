import jinja2
import sqlalchemy.sql.expression

from coolNewLanguage.src import consts
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util import db_utils


def template_from_select_statement(stmt: sqlalchemy.sql.expression.Select) -> str:
    """
    Construct an HTML table containing the results of the passed Select statement
    :param stmt: The select statement to run and render the results of
    :return: A string containing an HTML table containing the results
    """
    if not isinstance(stmt, sqlalchemy.sql.expression.Select):
        raise TypeError("Expected stmt to be a sqlalchemy Select")

    col_names = stmt.selected_columns.keys()
    # table contents
    with process.running_tool.db_engine.connect() as conn:
        rows = [row._mapping for row in conn.execute(stmt)]

    # get jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.TABLE_RESULT_TEMPLATE_FILENAME
    )
    # render and return it
    return template.render(col_names=col_names, rows=rows)


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

