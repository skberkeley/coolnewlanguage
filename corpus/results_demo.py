from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util import db_utils


def main():
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
        results.show_results([results.Result(created_table, "Created table:")])

    tool.add_stage('table_results', table_as_results)

    def column_list_as_results():
        col1 = ColumnSelectorComponent(label="Pick a column")
        col2 = ColumnSelectorComponent(label="Pick another")
        TableSelectorComponent("Pick a table to view columns from", [col1, col2])
        results.show_results([results.Result([col1, col2])])

    tool.add_stage('column_list_results', column_list_as_results)

    def cell_list_as_results():
        TextComponent("Select a column to get cells from:")
        col = ColumnSelectorComponent(label="Pick a column to get Cells from")
        TableSelectorComponent("Pick a table to select a column from", [col])

        my_results = []

        def get_cells():
            for cell in col:
                my_results.append(results.Result(cell))

        LambdaProcessor(get_cells)
        results.show_results(my_results)

    tool.add_stage('cell_list_results', cell_list_as_results)

    def row_list_as_results():
        table = TableSelectorComponent("Pick a table to get rows from")

        def get_rows():
            return [row for row in table]

        rows = LambdaProcessor(get_rows).result
        results.show_results([results.Result(rows)])

    tool.add_stage('row_list_results', row_list_as_results)

    tool.run()


if __name__ == '__main__':
    main()