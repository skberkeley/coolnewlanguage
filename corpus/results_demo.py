from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util import db_utils

tool = Tool('results_demo')

def table_as_results():
    TextComponent("Creating and displaying a table")
    def create_table():
        return db_utils.create_table_from_lists(
            "Names",
            [["First Name", "Last Name", "Age"], ["Oski", "Bear", "43"], ["Carol", "Christ", "500"]],
            return_existing_table=False,
            overwrite_existing_table=True
        )
    created_table = LambdaProcessor(create_table).result
    results.show_results(results.Result(created_table, "Created table:"))

tool.add_stage('table_results', table_as_results)

def column_list_as_results():
    col = ColumnSelectorComponent(label="Pick at least one column from a table")
    results.show_results(col)

tool.add_stage('column_list_results', column_list_as_results)

def row_list_as_results():
    table = TableSelectorComponent("Pick a table to get rows from")

    def get_rows():
        return [row for row in table]

    rows = LambdaProcessor(get_rows).result
    results.show_results(rows)

tool.add_stage('row_list_results', row_list_as_results)

tool.run()