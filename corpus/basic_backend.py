from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import create_table_from_csv


tool = Tool('basic_backend')

def csv_upload_and_name():
    """
    Stage to upload a csv file and give the resulting table a name. To test, upload a csv file, giving it a name,
    and then upload a non-csv file and make sure an error is shown. Finally, upload the original file and test that
    an error is shown regarding uploading a file with the same name.
    :return:
    """
    table_name = UserInputComponent(str, label="Enter table name:")
    csv_file = FileUploadComponent('csv', label="Upload a csv file:")

    def create_table():
        return create_table_from_csv(table_name, csv_file, True)
    created_table = LambdaProcessor(create_table).result
    results.show_results((created_table, "Created table: "))

tool.add_stage('csv_upload_and_name', csv_upload_and_name)

def table_viewer():
    """
    Stage to select and view a table. To test, access this stage after uploading a csv, and view a table. Verify
    all uploaded tables are viewable, and no hidden ones are.
    :return:
    """
    TextComponent("Select a table: ")
    table = TableSelectorComponent()
    results.show_results((table, "Selected table: "))

tool.add_stage('table_viewer', table_viewer)

def column_viewer():
    """
    Stage to select and view a column of a table. To test, access this stage after uploading a csv, select a table,
    and then select a column. Verify that metadata columns (those beginning with '__') are not selectable.
    :return:
    """
    TextComponent("Select a table and then select a column:")
    column_selector1 = ColumnSelectorComponent("Select a column:")
    column_selector2 = ColumnSelectorComponent("Select another column:")
    results.show_results((column_selector1, "Selected column: "), (column_selector2, "Selected column: "))

tool.add_stage('column_viewer', column_viewer)

def column_viewer_with_table():
    """
    Stage to select and view a column of a table. To test, access this stage after uploading a csv, select a table,
    and then select a column. Verify that metadata columns (those beginning with '__') are not selectable.
    :return:
    """
    TextComponent("Select a table and then select a column:")
    table = TableSelectorComponent()
    column_selector = ColumnSelectorComponent("Select a column:")
    results.show_results((table, "Selected table: "), (column_selector, "Selected column: "))
tool.add_stage('column_viewer_with_table', column_viewer_with_table)

tool.run()
