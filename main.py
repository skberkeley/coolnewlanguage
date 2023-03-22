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

    def matcher_stage():
        last_names_1 = ColumnSelectorComponent(label="Select the Last Name column", expected_val_type=str)
        first_names_1 = ColumnSelectorComponent(label="Select the First Name column", expected_val_type=str)
        mid_init_1 = ColumnSelectorComponent(label="Select the Middle Initial column", expected_val_type=str)
        table1 = TableSelectorComponent(columns=[last_names_1, first_names_1, mid_init_1])

        last_names_2 = ColumnSelectorComponent(label="Select the Last Name column", expected_val_type=str)
        first_names_2 = ColumnSelectorComponent(label="Select the First Name column", expected_val_type=str)
        mid_init_2 = ColumnSelectorComponent(label="Select the Middle Initial column", expected_val_type=str)
        table2 = TableSelectorComponent(columns=[last_names_2, first_names_2, mid_init_2])

        def match_cols():
            results = []
            for ln1, fn1, mi1 in zip(last_names_1, first_names_1, mid_init_1):
                for ln2, fn2, mi2 in zip(last_names_2, first_names_2, mid_init_2):
                    if ln1 == ln2 and fn1 == fn2 and mi1 == mi2:
                        results.append(f"{fn1} {mi1}. {ln1}")
            return results

        res = LambdaProcessor(match_cols).result
        show_results(res)
    tool.add_stage('matcher', matcher_stage)

    tool.run()


if __name__ == '__main__':
    main()
