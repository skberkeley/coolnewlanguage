import pandas as pd

import coolNewLanguage.src as hilt

tool = hilt.Tool('approvals_demo')

def approve_table_from_list_list():
    hilt.TextComponent("Creating and displaying a table to approve")

    if tool.user_input_received():
        df = pd.DataFrame([["Oski", "Bear", 1000], ["Carol", "Christ", 2000]], columns=["First Name", "Last Name", "Age"])
        tool.tables["Names"] = df

        hilt.approvals.get_user_approvals()
        hilt.results.show_results((tool.tables["Names"], "Created table: "))

tool.add_stage('table_results', approve_table_from_list_list)

def approve_table_deletion():
    table = hilt.TableSelectorComponent(label="Select table to delete")

    if tool.user_input_received():
        del tool.tables[table.table_name]

        hilt.approvals.get_user_approvals()

tool.add_stage('delete_table', approve_table_deletion)

tool.run()
