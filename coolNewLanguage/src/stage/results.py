from typing import List

import jinja2
import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.util.html_utils import template_from_select_statement


def show_results(result, label: str = '', results_title: str = '') -> None:
    """
    Render the passed result as a rendered Jinja template, and set it on Stage
    This function is called from the programmer defined stage functions, so
    returning wouldn't pass the state where we want it
    If we're not handling a post request, doesn't do anything
    :param result: The result to render in template
        Result could be an InputComponent, in which case we try to render its value
    :param label: An optional label for the results
    :param results_title: An optional title for the results webpage
    """
    if not isinstance(label, str):
        raise TypeError("Expected label to be a string")
    if not isinstance(results_title, str):
        raise TypeError("Expected results_title to be a string")

    # we're not handling a post request, so we don't have any results to show
    if not process.handling_post:
        return

    if isinstance(result, InputComponent):
        show_results(result.value, label, results_title)
        return

    match result:
        case sqlalchemy.Table():
            result = result_template_of_sql_alch_table(result)
        case [*cols] if all([isinstance(c, ColumnSelectorComponent) for c in cols]):
            result = result_template_of_column_list(cols)
        case [*cells] if all([isinstance(c, Cell) for c in cells]):
            result = result_template_of_cell_list(cells)
        case [*rows] if all([isinstance(r, Row) for r in rows]):
            result = result_template_of_row_list(rows)
        case _:
            result = str(result)

    if results_title == '':
        results_title = "Results"

    # load the jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.STAGE_RESULTS_TEMPLATE_FILENAME
    )
    # render the template and set it on Stage
    Stage.results_template = template.render(
        results_title=results_title,
        label=label,
        result=result
    )


def result_template_of_sql_alch_table(table: sqlalchemy.Table) -> str:
    """
    Construct an HTML snippet of a sqlalchemy Table
    :param table: The table to construct the template for
    :return: A string containing the HTML table the table with the table's data
    """
    if not isinstance(table, sqlalchemy.Table):
        raise TypeError("Expected table to be a sqlalchemy Table")

    stmt = sqlalchemy.select(table)

    return template_from_select_statement(stmt)


def result_template_of_column_list(cols: List[ColumnSelectorComponent]) -> str:
    """
    Construct an HTML snippet of some columns, all presumably from the same table
    Note: Current implementation assumes all string data
    :param cols: The columns to construct the HTML table for
    :return: A string containing the HTML table with the data from the columns
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


def result_template_of_cell_list(cells: List[Cell]) -> str:
    """
    Construct an HTML snippet of some cells, all assumed to be from the same table and column
    :param cells: The cells to render
    :return: A string containing an HTML table with the cells' data
    """
    if not isinstance(cells, list):
        raise TypeError("Expected cells to be a list")
    if not all([isinstance(cell, Cell) for cell in cells]):
        raise TypeError("Expected each element of cells to be a Cell")

    vals = []
    for cell in cells:
        val = cell.expected_type(cell.val) if cell.expected_type is not None else cell.val
        vals.append(str(val))

    # Get Jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.CELL_LIST_RESULT_TEMPLATE_FILENAME
    )
    # Render and return template
    return template.render(vals=vals)


def result_template_of_row_list(rows: List[Row]) -> str:
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
        name=consts.SELECT_STMT_RESULT_TEMPLATE_FILENAME
    )
    # Render and return template
    return template.render(col_names=col_names, rows=jinja_rows)

