import pandas as pd

from coolNewLanguage.src.approvals import approvals
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool

tool = Tool('approvals_demo')

def approve_table_from_list_list():
    TextComponent("Creating and displaying a table to approve")

    if tool.user_input_received():
        df = pd.DataFrame([["Oski", "Bear", 1000], ["Carol", "Christ", 2000]], columns=["First Name", "Last Name", "Age"])
        tool.tables["Names"] = df

        approvals.get_user_approvals()

tool.add_stage('table_results', approve_table_from_list_list)

def approve_table_deletion():
    table = TableSelectorComponent(label="Select table to delete")

    if tool.user_input_received():
        del tool.tables[table.table_name]

        approvals.get_user_approvals()

tool.add_stage('delete_table', approve_table_deletion)

tool.run()
