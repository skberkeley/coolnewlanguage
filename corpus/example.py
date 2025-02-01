import pandas as pd

from coolNewLanguage.src import ColumnSelectorComponent, FileUploadComponent, SelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool

tool = Tool('bug')

def create_df():

    if tool.user_input_received():
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        tool.tables["test"] = df
        results.show_results((df, "saved initial dataframe"))

tool.add_stage('create_df', create_df)


tool.run()