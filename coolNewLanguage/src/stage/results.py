from typing import List, Any

import jinja2
import pandas as pd
import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.cell import Cell
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.util import html_utils, link_utils, db_utils


class Result:
    """
    An object-based representation of a result, label pairing
    The value has already been converted by HTML, presumably by one of the helper functions in this file
    Attributes:
        html_value: An HTML representation of this Result's value, to be rendered later
        label: An optional label for the value to display
    """
    __slots__ = ('value', 'label', 'html_value')

    def __init__(self, value: Any, label: str = ''):
        """

        :param value: The value to display for this Result
        :param label: An optional label to display with the value
        """
        if not process.handling_post:
            return

        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        self.value = value
        self.label = label

    def __eq__(self, other):
        if isinstance(other, Result):
            return self.value == other.value and self.label == other.label
        return False


def show_results(*results: Any, results_title: str = '') -> None:
    """
    Render the passed results as a rendered Jinja template, setting it on Stage when done.
    This function is called from the programmer defined stage functions, so
    returning wouldn't pass the state where we want it.
    If we're not handling a post request, doesn't do anything
    :param results: The results to render, a list of Result objects
    :param results_title: An optional title for the results webpage
    """
    if not isinstance(results_title, str):
        raise TypeError("Expected results_title to be a string")

    # we're not handling a post request, so we don't have any results to show
    if not process.handling_post and not process.handling_user_approvals:
        return

    result_objects = []
    for result in results:
        match result:
            case Result():
                result_objects.append(result)
            case (value, str(label)):
                result_objects.append(Result(value, label))
            case _:
                result_objects.append(Result(result))

    # if process.get_user_approvals is set to True, cache the results to show then return, since we want to collect user
    # approvals first
    if process.get_user_approvals:
        process.cached_show_results = result_objects
        process.cached_show_results_title = results_title
        return

    if results_title == '':
        results_title = "Results"

    # render each Result
    for result in result_objects:
        result.html_value = result_template_of_value(result.value)

    # load the jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.STAGE_RESULTS_TEMPLATE_FILENAME
    )
    # render the template and set it on Stage
    Stage.results_template = template.render(
        results_title=results_title,
        results=result_objects
    )


def result_template_of_value(value) -> str:
    """
    Helper function return HTML snippet to show value within result template.
    :param value:
    :return:
    """

    match value:
        case sqlalchemy.Table():
            return result_template_of_sql_alch_table(value)
        case ColumnSelectorComponent() as cols:
            return result_template_of_column_list(cols)
        case [*cells] if all([isinstance(c, Cell) for c in cells]):
            return result_template_of_cell_list(cells)
        case [*rows] if all([isinstance(r, Row) for r in rows]):
            return result_template_of_row_list(rows)
        case [*rows] if all([isinstance(r, list) for r in rows]):
            return result_template_of_list_list(rows)
        case ColumnSelectorComponent():
            return result_template_of_column_list([value])
        case InputComponent():
            return result_template_of_value(value.value)
        case Link():
            return result_template_of_link(value)
        case [*links] if all(isinstance(l, Link) for l in links):
            return "\n".join(result_template_of_link(l) for l in links)
        case pd.DataFrame():
            return result_template_of_dataframe(value)
        case _:
            return str(value)


def result_template_of_sql_alch_table(table: sqlalchemy.Table) -> str:
    """
    Construct an HTML snippet of a sqlalchemy Table
    If the table doesn't exist in the underlying db, returns an emtpy string
    :param table: The table to construct the template for
    :return: A string containing the HTML table the table with the table's data
    """
    # Check to see if the table exists in the db
    process.running_tool.db_metadata_obj = sqlalchemy.MetaData()
    process.running_tool.db_metadata_obj.reflect(process.running_tool.db_engine)
    if table.name not in process.running_tool.db_metadata_obj.tables:
        return ""

    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.TABLE_RESULT_TEMPLATE_FILENAME
    )
    return html_utils.html_of_table(table, template)


def result_template_of_column_list(cols: ColumnSelectorComponent) -> str:
    """
    Construct an HTML snippet of some columns, all presumably from the same table
    Note: Current implementation assumes all string data
    :param cols: The columns to construct the HTML table for
    :return: A string containing the HTML table with the data from the columns
    """
    if not isinstance(cols, ColumnSelectorComponent):
        raise TypeError("Expected cols to be a ColumnSelectorComponent")

    table: sqlalchemy.Table = process.running_tool.get_table_from_table_name(cols.table_name)
    sqlalchemy_cols = [table.c[col] for col in cols.value]
    stmt = sqlalchemy.select(*sqlalchemy_cols)

    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.TABLE_RESULT_TEMPLATE_FILENAME
    )

    return html_utils.template_from_select_statement(stmt, template, table_name=cols.table_name)


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
    return html_utils.html_of_row_list(rows)


def result_template_of_list_list(rows: list[list]) -> str:
    """
    Construct an HTML snippet of a table passed as a list of lists. Calls str() on each value to convert to HTML.
    Assumes the first row contains column names.
    :param rows: The rows of the table to render
    :return: A string containing an HTML table with the data from rows
    """
    if not isinstance(rows, list):
        raise TypeError("Expected rows to be a list")
    if not all(map(lambda l: isinstance(l, list), rows)):
        raise TypeError("Expected each member of rows to be a list")
    if not all(map(lambda l: len(l) == len(rows[0]), rows[1:])):
        raise ValueError("Expected each member of rows to have the same length")

    col_names = rows[0]
    jinja_rows = [{col_name: str(row[i]) for i, col_name in enumerate(col_names)} for row in rows[1:]]

    # Get Jinja template
    template: jinja2.Template = process.running_tool.jinja_environment.get_template(
        name=consts.TABLE_RESULT_TEMPLATE_FILENAME
    )
    # Render and return template
    return template.render(col_names=col_names, rows=jinja_rows)


def result_template_of_link(link: Link) -> str:
    """
    Construct an HTML snippet of a link
    :param link: The link to render
    :return: A string containing an HTML table with the data from the link
    """
    # Check if link exists
    link_id = link.link_id
    if link_id is None:
        link_id = link_utils.get_link_id(
            process.running_tool,
            link.link_meta_id,
            link.src_table_name,
            link.src_row_id,
            link.dst_table_name,
            link.dst_row_id
        )
    # If it doesn't, return an empty string
    if link_id is None:
        return ""

    return html_utils.html_of_link(link)

def result_template_of_dataframe(df: pd.DataFrame) -> str:
    """
    Construct an HTML snippet of a pandas DataFrame
    :param df:
    :return:
    """
    return df.to_html()
