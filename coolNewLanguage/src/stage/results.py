from typing import List

import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.stage import process

"""
The rendered Jinja template containing any relevant results
Set here by show_results() so that we have access
to it outside the scope of the stage_func call
"""
results_template = None


def show_results(result, label: str = ''):
    """
    Render the passed result as a rendered Jinja template, and set it on Stage
    This function is called from the programmer defined stage functions, so
    returning wouldn't pass the state where we want it
    If we're not handling a post request, doesn't do anything
    :param result: The result to render in template
        Result could be an InputComponent, in which case we try to render its value
    :param label: An optional label for the results
    """
    # we're not handling a post request, so we don't have any results to show
    if not process.handling_post:
        return

    if isinstance(result, InputComponent):
        show_results(result.value, label)
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
    global results_template
    results_template = jinja_template.render()


def result_template_of_sql_alch_table(table: sqlalchemy.Table) -> List[str]:
    """
    Construct an HTML template of a sqlalchemy Table
    Note: Current implementation assumes all string data
    :param table: The table to construct the template for
    :return: A list of HTML components comprising the table with the table's data
    """
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected a sqlalchemy Table for table")

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
    with process.running_tool.db_engine.connect() as conn:
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
