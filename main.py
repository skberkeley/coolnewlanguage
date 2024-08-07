import pandas as pd

from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool

tool = Tool('main_test')

def csv_upload_and_name():
    """
    Stage to upload a csv file and give the resulting table a name. To test, upload a csv file, giving it a name,
    and then upload a non-csv file and make sure an error is shown. Finally, upload the original file and test that
    an error is shown regarding uploading a file with the same name.
    :return:
    """
    table_name = UserInputComponent(str, label="Enter table name:")
    csv_file = FileUploadComponent('csv', label="Upload a csv file:")

    if tool.user_input_received():
        df = pd.read_csv(csv_file.value)
        tool.tables[table_name.value] = df

        results.show_results((df, "Created table: "))

tool.add_stage('csv_upload_and_name', csv_upload_and_name)

def view_tables():
    table = TableSelectorComponent("Pick a table to view")

    if tool.user_input_received():
        results.show_results((table, 'Chosen table: '))

tool.add_stage('view_tables', view_tables)

def pick_columns():
    cols = ColumnSelectorComponent("Pick some columns", num_columns=2)

    if tool.user_input_received():
        results.show_results((cols, 'Chosen columns: '))

tool.add_stage('pick_columns', pick_columns)

tool.run()