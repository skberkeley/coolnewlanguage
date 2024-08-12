import pandas as pd

import coolNewLanguage.src as hilt

tool = hilt.Tool('basic_backend')

def csv_upload_and_name():
    """
    Stage to upload a csv file and give the resulting table a name. To test, upload a csv file, giving it a name,
    and then upload a non-csv file and make sure an error is shown. Finally, upload the original file and test that
    an error is shown regarding uploading a file with the same name.
    :return:
    """
    table_name = hilt.UserInputComponent(str, label="Enter table name:")
    csv_file = hilt.FileUploadComponent('.csv', label="Upload a csv file:")

    if tool.user_input_received():
        df = pd.read_csv(csv_file.value)
        tool.tables[table_name.value] = df

        hilt.results.show_results((df, "Created table: "))


tool.add_stage('csv_upload_and_name', csv_upload_and_name)

def table_viewer():
    """
    Stage to select and view a table. To test, access this stage after uploading a csv, and view a table. Verify
    all uploaded tables are viewable, and no hidden ones are.
    :return:
    """
    hilt.TextComponent("Select a table: ")
    table = hilt.TableSelectorComponent()
    if tool.user_input_received():
        hilt.results.show_results((table, "Selected table: "))

tool.add_stage('table_viewer', table_viewer)

def column_viewer():
    """
    Stage to select and view a column of a table. To test, access this stage after uploading a csv, select a table,
    and then select a column. Verify that metadata columns (those beginning with '__') are not selectable.
    :return:
    """
    hilt.TextComponent("Select a table and then select a column:")
    column_selector1 = hilt.ColumnSelectorComponent("Select a column:")
    column_selector2 = hilt.ColumnSelectorComponent("Select another column:")
    if tool.user_input_received():
        hilt.results.show_results((column_selector1, "Selected column: "), (column_selector2, "Selected column: "))

tool.add_stage('column_viewer', column_viewer)

def column_viewer_with_table():
    """
    Stage to select and view a column of a table. To test, access this stage after uploading a csv, select a table,
    and then select a column. Verify that metadata columns (those beginning with '__') are not selectable.
    :return:
    """
    hilt.TextComponent("Select a table and then select a column:")
    table = hilt.TableSelectorComponent()
    column_selector = hilt.ColumnSelectorComponent("Select a column:")
    if tool.user_input_received():
        hilt.results.show_results((table, "Selected table: "), (column_selector, "Selected column: "))
tool.add_stage('column_viewer_with_table', column_viewer_with_table)


def copy_bug():
    table_name = hilt.UserInputComponent(str, label="Enter new table name: ")
    table = hilt.TableSelectorComponent()
    col = hilt.ColumnSelectorComponent()
    file = hilt.FileUploadComponent('csv')
    selector = hilt.SelectorComponent(['1', '2', '3'])
    if tool.user_input_received():
        print(table_name.value)
        print(table.table_name)
        print(col.table_name)
        print(file.value)
        print(selector.value)

tool.add_stage('copy_bug', copy_bug)

tool.run()
