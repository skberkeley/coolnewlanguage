import numpy as np
import pandas as pd

import coolNewLanguage.src as hilt

tool = hilt.Tool('approvals_demo')

def approve_table_from_list_list():
    hilt.TextComponent("Creating and displaying a table to approve")

    if tool.user_input_received():
        df = pd.DataFrame(
            [
                ["L", "Hamilton", 2025],
                ["M", "Verstappen", 2016],
                ["C", "Leclerc", 2019]
            ],
            columns=["First Name", "Last Name", "Year Joined"]
        )
        tool.tables["Ferrari Drivers"] = df

        hilt.approvals.get_user_approvals()
        hilt.results.show_results((tool.tables["Ferrari Drivers"], "Created table: "))

tool.add_stage('table_results', approve_table_from_list_list)

def approve_table_deletion():
    table = hilt.TableSelectorComponent(label="Select table to delete")

    if tool.user_input_received():
        del tool.tables[table.table_name]

        hilt.approvals.get_user_approvals()

tool.add_stage('delete_table', approve_table_deletion)

def approve_column_addition():
    table = hilt.TableSelectorComponent(label="Select table to add column to")

    if tool.user_input_received():
        df = table.value
        df = df.assign(NewColumn=np.random.randint(0, 100, df.shape[0]))
        tool.tables[table.table_name] = df

        hilt.approvals.get_user_approvals()

tool.add_stage('add_column', approve_column_addition)

tool.run()
