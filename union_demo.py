import coolNewLanguage.src as hilt
import pandas as pd

tool = hilt.Tool('UnionRegistrations')

tool.tables['University Roster'] = pd.DataFrame(
    columns=['Name', 'Email', 'Grad Year'])
tool.tables['Union Roster'] = pd.DataFrame(
    columns=['Name', 'Email', 'Grad Year'])


def file_upload():
    file_path = hilt.FileUploadComponent(
        expected_ext="csv", label="Input a CSV file", replace_existing=True)
    name_input = hilt.UserInputComponent(str, "Name your CSV file: ")
    if tool.user_input_received():
        hilt.results.show_results((file_path.value, "Uploaded file path: "))
        df = pd.read_csv(file_path.value)
        tool.tables[name_input.value] = df


tool.add_stage('File Upload', file_upload)


def extend_roster():
    roster_selector = hilt.SelectorComponent(
        options=['University Roster', 'Union Roster'], label='Choose a roster to extend:')
    name_col = hilt.ColumnSelectorComponent(
        "Choose the column with names:")
    email_col = hilt.ColumnSelectorComponent(
        "Choose the column with emails:")
    grad_year_col = hilt.ColumnSelectorComponent(
        "Choose the column with grad years:")
    if tool.user_input_received():
        roster_name = roster_selector.value
        names, emails, grad_years = name_col.value, email_col.value, grad_year_col.value

        new_rows = pd.DataFrame({'Name': names.to_numpy().flatten(),
                                'Email': emails.to_numpy().flatten(),
                                 'Grad Year': grad_years.to_numpy().flatten()})

        tool.tables[roster_name] = pd.concat(
            [tool.tables[roster_name], new_rows], ignore_index=True)
        hilt.approvals.get_user_approvals()
        hilt.results.show_results(
            (tool.tables[roster_name], "Extended roster: "))


tool.add_stage('Extend Roster', extend_roster)


def compute_matches():
    hilt.SubmitComponent("Compute Matches")
    if tool.user_input_received():
        year_email_matches = tool.tables['University Roster'].merge(tool.tables['Union Roster'], on=[
            'Email', 'Grad Year'], how='inner', suffixes=['_university', '_union'])
        tool.tables['Matches'] = year_email_matches
        hilt.approvals.get_user_approvals()
        hilt.results.show_results((tool.tables['Matches'], "Matches: "))


tool.add_stage('Compute Matches', compute_matches)


tool.run()
