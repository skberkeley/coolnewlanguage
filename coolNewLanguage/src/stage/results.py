from typing import List

import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.util.html_utils import template_from_select_statement


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
        case [*cols] if all([isinstance(c, ColumnSelectorComponent) for c in cols]):
            template_list += result_template_of_column_list(cols)
        case [*cells] if all([isinstance(c, Cell) for c in cols]):
            template_list += result_template_of_cell_list(cells)
        case [*rows] if all([isinstance(r, Row) for r in rows]):
            template_list += result_template_of_row_list(rows)
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

    stmt = sqlalchemy.select(table)

    return template_from_select_statement(stmt)


def result_template_of_column_list(cols: List[ColumnSelectorComponent]) -> List[str]:
    """
    Construct an HTML template of some columns, all presumably from the same table
    Note: Current implementation assumes all string data
    :param cols: The table to construct the template for
    :return: A list of HTML components comprising the table with the table's data
    :param cols:
    :return:
    """
    if not isinstance(cols, list):
        raise TypeError("Expected cols to be a list")
    if not all([isinstance(c, ColumnSelectorComponent) for c in cols]):
        raise TypeError("Expected each element of cols to be a ColumnSelectorComponent")
    if any([c.table_selector is None for c in cols]):
        raise ValueError("Each column in cols should have an associated TableSelectorComponent")
    if len(set([c.table_selector for c in cols])) > 1:
        raise ValueError("Each column in cols should be associated with the same TableSelectorComponent")

    table: sqlalchemy.Table = cols[0].table_selector.value
    sqlalchemy_cols = [table.c[col.emulated_column] for col in cols]
    stmt = sqlalchemy.select(*sqlalchemy_cols)

    return template_from_select_statement(stmt)


def result_template_of_cell_list(cells: List[Cell]) -> List[str]:
    """
    Construct an HTML template of some cells, all assumed to be from the same table and column
    :param cells: The cells to render
    :return:
    """
    if not isinstance(cells, list):
        raise TypeError("Expected cells to be a list")
    if not all([isinstance(cell, Cell) for cell in cells]):
        raise TypeError("Expected each element of cells to be a Cell")

    template_list = ['<table>']
    for cell in cells:
        template_list.append('<tr>')
        template_list.append('<td>')

        val = cell.expected_type(cell.val) if cell.expected_type is not None else cell.val

        template_list.append(str(val))

        template_list.append('</td>')
        template_list.append('</tr>')
    template_list.append('</table>')

    return template_list


def result_template_of_row_list(rows: List[Row]) -> List[str]:
    """
    Construct an HTML template of some rows, all assumed to be from the same table
    :param rows: 
    :return: 
    """
    if not isinstance(rows, list):
        raise TypeError("Expected rows to be a list")
    if not all([isinstance(r, Row) for r in rows]):
        raise TypeError("Expected each element of rows to be a Row")
    
    template_list = ['<table>']
    col_names = rows[0].keys()
    # header
    template_list.append('<tr>')
    for col in col_names:
        template_list.append('<th>')
        template_list.append(col)
        template_list.append('</th>')
    template_list.append('</tr>')
    # contents
    for row in rows:
        template_list.append('<tr>')
        for col in col_names:
            template_list.append('<td>')
            template_list.append(str(row[col]))
            template_list.append('</td>')
        template_list.append('</tr>')
    # finish out list and return
    template_list.append('</table>')

    return template_list

