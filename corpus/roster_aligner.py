import pandas as pd

from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool


tool = Tool('roster_aligner')

# First, we need a stage where users can upload datasets
def dataset_upload_stage():
    # The preamble of a stage consists of component declarations, some (or all) of which are user input fields
    file_upload_input = FileUploadComponent('csv', "Upload new data sets here:")
    dataset_name_input = UserInputComponent(str, "Enter a name for the dataset you're uploading:")
    # Next, we use a Processor to do stuff with these inputs
    if tool.user_input_received():
        df = pd.read_csv(file_upload_input.value)
        tool.tables[dataset_name_input.value] = df
        # To show the results, call show_results
        results.show_results(df)

# After defining the stage, we add it to our Tool
tool.add_stage('dataset_upload', dataset_upload_stage)

# Next we define a stage where users can perform some simple matching
# For this example, we'll let them choose the columns corresponding to first name and last name from two different
# datasets, and return all the rows where names match
def simple_column_matcher():
    # First, we define the inputs the user will provide using Components
    # Users select columns using ColumnSelectorComponents
    c1 = ColumnSelectorComponent("Choose the column containing names from one dataset")

    c2 = ColumnSelectorComponent("Choose the column containing names from another dataset")

    if tool.user_input_received():
        # The code in this function is run after users have submitted their inputs
        # This lets us do things like join the two DataFrames
        matches = pd.merge(c1.value, c2.value, how='inner', left_on=c1.column_names, right_on=c2.column_names)

        # If we didn't find any matches, return a string saying so
        if len(matches) == 0:
            results.show_results("No matches found")
        # We then display the results to the user
        results.show_results(matches)

tool.add_stage('simple_matcher', simple_column_matcher)

# A stage just to view the tables that exist in this tool's backend
def table_viewer():
    # Use a TableSelectorComponent so that users can select the table they want to view
    table = TableSelectorComponent("Select a table to view")

    if tool.user_input_received():
        # In this case, we don't need to do anything extra with the table, and can display it right away
        results.show_results(table)

tool.add_stage('table_viewer', table_viewer)

# Make sure to run the tool
tool.run()
