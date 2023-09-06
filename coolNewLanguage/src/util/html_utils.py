from typing import List

import jinja2
import sqlalchemy.sql.expression

from coolNewLanguage.src import consts
from coolNewLanguage.src.stage import process


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
