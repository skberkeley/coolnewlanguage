from typing import List

import sqlalchemy.sql.expression

from coolNewLanguage.src.stage import process


def template_from_select_statement(stmt: sqlalchemy.sql.expression.Select) -> List[str]:
    """
    Construct a template for an HTML table containing the results of the passed Select statement
    :param stmt: The select statement to run and render the results of
    :return: A template with an HTML table containing the results
    """
    if not isinstance(stmt, sqlalchemy.sql.expression.Select):
        raise TypeError("Expected stmt to be a sqlalchemy Select statement")

    col_names = stmt.selected_columns.keys()

    template_list = ['<table>']

    # header row
    template_list.append('<tr>')
    for col in col_names:
        template_list.append('<th>')
        template_list.append(col)
        template_list.append('</th>')
    template_list.append('</tr>')
    # table contents
    with process.running_tool.db_engine.connect() as conn:
        for row in conn.execute(stmt):
            template_list.append('<tr>')
            row_map = row._mapping
            for col in col_names:
                template_list.append('<td>')
                template_list.append(str(row_map[col]))
                template_list.append('</td>')
            template_list.append('</tr>')
    # finish out list and return
    template_list.append('</table>')

    return template_list
