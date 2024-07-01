from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util import db_utils


tool = Tool('roster_aligner')

# First, we need a stage where users can upload datasets
def dataset_upload_stage():
    # The preamble of a stage consists of component declarations, some (or all) of which are user input fields
    file_upload_input = FileUploadComponent('csv', "Upload new data sets here:")
    dataset_name_input = UserInputComponent(str, "Enter a name for the dataset you're uploading:")
    # Next, we use a Processor to do stuff with these inputs
    def save_dataset():
        saved_table = db_utils.create_table_from_csv(dataset_name_input, file_upload_input)
        return saved_table
    # Instantiating a Processor ensures the code is run after the user is finished inputting
    processor = LambdaProcessor(save_dataset)
    # We use the result property to access the return value of the function called by the LambdaProcessor
    # To show a result later, we can place it in a Result object
    my_result = results.Result(processor.result, "Here is the saved dataset: ")
    # To show the results, call show_results on a list of Result objects
    results.show_results(my_result)

# After defining the stage, we add it to our Tool
tool.add_stage('dataset_upload', dataset_upload_stage)

# Next we define a stage where users can perform some simple matching
# For this example, we'll let them choose the columns corresponding to first name and last name from two different
# datasets, and return all the rows where names match
def simple_column_matcher():
    # First, we define the inputs the user will provide using Components
    # Users select columns using ColumnSelectorComponents
    c1 = ColumnSelectorComponent("Choose the column containing names from one dataset")
    t1 = TableSelectorComponent("Choose the table you picked from")

    c2 = ColumnSelectorComponent("Choose the column containing names from another dataset")
    t2 = TableSelectorComponent("Choose the table you picked from")

    # Next we use a function to outline what should be done with those inputs
    def do_simple_match():
        # In this function, we build up a table of matches using a list of lists
        # The first row will contain the column names of the table we're building
        matches_table = [["Name"]]
        # The code in this function is run after users have submitted their inputs
        # This lets us do things like iterating over the rows of a table:
        for row1 in t1:
            # We can also index into a row of a table using column names
            name1 = row1[c1.value[0]]
            for row2 in t2:
                name2 = row2[c2.value[0]]

                if name1 == name2:
                    matches_table.append([name1])

        # If we didn't find any matches, return a string saying so
        if len(matches_table) == 1:
            return "No matches found"
        # Return the matches we found so that we have access to them after this function returns
        return matches_table

    # Again, we pass the function into a LambdaProcessor
    processor = LambdaProcessor(do_simple_match)
    # We then display the results to the user
    results.show_results(results.Result(processor.result))

tool.add_stage('simple_matcher', simple_column_matcher)

# A stage just to view the tables that exist in this tool's backend
def table_viewer():
    # Use a TableSelectorComponent so that users can select the table they want to view
    table = TableSelectorComponent("Select a table to view")
    # In this case, we don't need to do anything extra with the table, and can display it right away
    results.show_results(table)

tool.add_stage('table_viewer', table_viewer)



# Make sure to run the tool
tool.run()
