from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent, TableSelectorComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.processor.map_processor import MapProcessor
from coolNewLanguage.src.stage.results import show_results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import create_table_from_csv


def main():
    """engine = sqlalchemy.create_engine('sqlite:///test.db', echo=True)
    metadata = sqlalchemy.MetaData()
    with open('coolNewLanguage/static/test_data/FY2017_Short.csv') as csv_file:
        table = table_from_csv_file("test table", csv_file, metadata, True)
        metadata.create_all(engine)
        insert_stmt = insert_into_table_from_csv_file(table, csv_file, True)
    with engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()"""
    tool = Tool('uploader')

    def upload_stage():
        table_name = UserInputComponent(str, label="Enter table name:")
        csv_file = FileUploadComponent('csv', label="Upload the csv:")

        def create_table():
            return create_table_from_csv(table_name, csv_file, True)
        LambdaProcessor(create_table)

    tool.add_stage('upload_stage', upload_stage)

    def table_selector_stage():
        TextComponent("Pick a table:")
        table = TableSelectorComponent()
        show_results(table, label="Selected table:")
    tool.add_stage('table_selector', table_selector_stage)

    def print_items_in_col_through_table():
        c = ColumnSelectorComponent(label="Select a column")
        table = TableSelectorComponent(columns=[c])

        def get_last_names():
            results = []
            for row in table:
                results.append(row[c.emulated_column])
            return results
        p = LambdaProcessor(get_last_names)
        show_results(p.result)
    tool.add_stage('print_col', print_items_in_col_through_table)

    def matcher():
        last_names_1 = ColumnSelectorComponent(label="Select the Last Name column", expected_val_type=str)
        first_names_1 = ColumnSelectorComponent(label="Select the First Name column", expected_val_type=str)
        mid_init_1 = ColumnSelectorComponent(label="Select the Middle Initial column", expected_val_type=str)
        table1 = TableSelectorComponent(columns=[last_names_1, first_names_1, mid_init_1])

        last_names_2 = ColumnSelectorComponent(label="Select the Last Name column", expected_val_type=str)
        first_names_2 = ColumnSelectorComponent(label="Select the First Name column", expected_val_type=str)
        mid_init_2 = ColumnSelectorComponent(label="Select the Middle Initial column", expected_val_type=str)
        table2 = TableSelectorComponent(columns=[last_names_2, first_names_2, mid_init_2])

        def do_match():
            results = []
            for row1 in table1:
                for row2 in table2:
                    ln1 = row1[last_names_1]
                    ln2 = row2[last_names_2]
                    fn1 = row1[first_names_1]
                    fn2 = row2[first_names_2]
                    mi1 = row1[mid_init_1]
                    mi2 = row2[mid_init_2]
                    if ln1 == ln2 and fn1 == fn2 and mi1 == mi2:
                        results.append(row1)
            return results
        p = LambdaProcessor(do_match)
        show_results(p.result)
    tool.add_stage('matcher', matcher)

    def filter_then_map():
        borough = ColumnSelectorComponent(label="Select the borough column", expected_val_type=str)
        ot_hours = ColumnSelectorComponent(label="Select the OT hours column", expected_val_type=int)
        table = TableSelectorComponent(columns=[borough, ot_hours])
        def do_filter():
            return list(filter(lambda r: r[borough] == "MANHATTAN", table))
        filter_p = LambdaProcessor(do_filter)
        def do_map():
            return [r[ot_hours] * 5 for r in filter_p.result]
        map_p = LambdaProcessor(do_map)
        show_results(map_p.result)
    tool.add_stage('filter_then_map', filter_then_map)

    tool.run()


if __name__ == '__main__':
    main()
