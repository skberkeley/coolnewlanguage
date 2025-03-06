import coolNewLanguage.src as hilt
import pandas as pd
def coords_to_county(lat: str, lon: str):
    import json
    with open('counties.json') as f:
        counties = json.load(f)
    return counties[f'{lat}, {lon}']

tool = hilt.Tool('Wildfires')
def file_upload():
    file_path = hilt.FileUploadComponent(expected_ext = "csv", label = "Input a CSV file", replace_existing=True)
    name_input = hilt.UserInputComponent(str, "Name your CSV file: ")
    if tool.user_input_received():
        hilt.results.show_results((file_path.value, "Uploaded file path: "))
        df = pd.read_csv(file_path.value)
        tool.tables[name_input.value] = df
tool.add_stage('File Upload', file_upload)
def add_county():
    lat_selector = hilt.ColumnSelectorComponent("Choose your latitude column:")
    lon_selector = hilt.ColumnSelectorComponent("Choose your longitude column:")
    if tool.user_input_received():
        lat_col = lat_selector.column_names[0]
        lon_col = lon_selector.column_names[0]
        df = tool.tables[lat_selector.table_name]
        table_name = lat_selector.table_name
        df['COUNTY'] = df.apply(lambda row: coords_to_county(row[lat_col], row[lon_col]), axis=1)
        tool.tables[table_name] = df
        hilt.approvals.get_user_approvals()
        hilt.results.show_results((tool.tables[table_name], "Added counties to table: "))
def match_facilities():
    facilities_selector = hilt.ColumnSelectorComponent("Choose columns from the facilities dataset:")
    fire_selector = hilt.ColumnSelectorComponent("Choose columns from the fire dataset:")
    county_selector = hilt.ColumnSelectorComponent("Choose the county column from a facility dataset:")
    if tool.user_input_received():
        matched_df = pd.DataFrame()
        match_col = county_selector.column_names[0]
        facilities_cols = facilities_selector.column_names
        fire_cols = fire_selector.column_names

        filtered_facilities_df = tool.tables[facilities_selector.table_name][[match_col] + facilities_cols]
        filtered_fire_df = tool.tables[fire_selector.table_name][[match_col] + fire_cols]

        matched_df = pd.merge(filtered_facilities_df, filtered_fire_df, on=match_col)
        tool.tables['matched_df'] = matched_df
        hilt.approvals.get_user_approvals()
        hilt.results.show_results((tool.tables['matched_df'], "Created new matched table: "))
tool.add_stage('Add County', add_county)
tool.add_stage('Match Facilities', match_facilities)
tool.run()





