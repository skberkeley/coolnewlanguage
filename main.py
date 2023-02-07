from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.table_selector import *
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
            return create_table_from_csv(table_name, csv_file, tool)
        LambdaProcessor(create_table)

    tool.add_stage('upload_stage', upload_stage)

    def table_selector_demo_stage():
        TextComponent("Pick a table:")
        columns = [
            ColumnSelector(label=f"Select column {str(i)}...") 
            for i in range(3)
        ]

        table = TableSelector(tool=tool, columns=columns)

        def done():
            columns_str = ', '.join([str(column) for column in columns])
            print("Got table", table, "and columns", columns_str)
        LambdaProcessor(done)
    tool.add_stage('table_selector_demo', table_selector_demo_stage)

    tool.run()


if __name__ == '__main__':
    main()
