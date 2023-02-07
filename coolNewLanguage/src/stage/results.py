from typing import List

import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.stage.stage import Stage


def show_results(result, label: str = ''):
    """
    Render the passed result as a rendered Jinja template, and set it on Stage
    This function is called from the programmer defined stage functions, so
    returning wouldn't pass the state where we want it
    If we're not handling a post request, doesn't do anything
    :param result: The result to render in template
    :param label: An optional label for the results
    """
    # we're not handling a post request, so we don't have any results to show
    if not Stage.handling_post:
        return

    form_action = '/'
    form_method = "get"

    template_list = [
        '<html>',
        '<head>',
        '<title>',
        "Results",
        '</title>',
        '</head>',
        '<body>',
    ]

    if label:
        template_list += [
            '<div>',
            '<p>',
            label,
            '</p>',
            '</div>'
        ]

    template_list.append('<div>')

    match result:
        case sqlalchemy.Table():
            template_list += result_template_of_sql_alch_table(result)
        case _:
            template_list.append(str(result))

    template_list += [
        '</div>',
        f'<form action="{form_action}" method="{form_method}">',
        '<input type="submit" value="Back to landing page">',
        '</form>',
        '</body>',
        '</html>'
    ]

    raw_template = ''.join(template_list)
    jinja_template = consts.JINJA_ENV.from_string(raw_template)
    Stage.results_template = jinja_template.render()


def result_template_of_sql_alch_table(table: sqlalchemy.Table) -> List[str]:
    """
    Construct an HTML template of a sqlalchemy Table
    Note: Current implementation assumes all string data
    :param table: The table to construct the template for
    :return: A list of HTML components comprising the table with the table's data
    """
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected a sqlalchemy Table for table")
    if not hasattr(table, 'engine'):
        raise ValueError("Expected the table to have an associated engine")

    col_names = table.columns.keys()
    stmt = sqlalchemy.select(table)

    template_list = ['<table>']

    # header row
    template_list.append('<tr>')
    for col in col_names:
        template_list.append('<th>')
        template_list.append(col)
        template_list.append('</th>')
    template_list.append('</tr>')
    # table contents
    with table.engine.connect() as conn:
        for row in conn.execute(stmt):
            template_list.append('<tr>')
            row_map = row._mapping
            for col in col_names:
                template_list.append('<td>')
                template_list.append(row_map[col])
                template_list.append('</td>')
            template_list.append('</tr>')
    # finish out list and return
    template_list.append('</table>')

    return template_list
