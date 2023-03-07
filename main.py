from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent, TableSelectorComponent, \
    create_column_selector_from_table_selector
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.column_xproduct_processor import ColumnXProductProcessor
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.stage.results import show_results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import create_table_from_csv


def two_column_select(label: str):
    c_a = ColumnSelectorComponent(label=f"{label} Column 1")
    c_b = ColumnSelectorComponent(label=f"{label} Column 2")
    table = TableSelectorComponent(label=label, columns=[c_a, c_b])
    return table, c_a, c_b


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

    def table_selector_demo_stage():
        TextComponent("Pick a table:")
        columns = [
            ColumnSelectorComponent(label=f"Select column {str(i)}...")
            for i in range(3)
        ]

        table = TableSelectorComponent(columns=columns)

        show_results(columns)
    tool.add_stage('table_selector_demo', table_selector_demo_stage)

    def two_select_stage():
        TextComponent("Select two tables and two columns each to corelate on:")
        t1, c1_1, c1_2 = two_column_select(label="Table 1")
        t2, c2_1, c2_2 = two_column_select(label="Table 2")

        def done():
            print("Got tables", t1, t2)
        LambdaProcessor(done)
    tool.add_stage("two_select_stage", two_select_stage)

    def add_one():
        TextComponent("This tool adds one to each element of the selected column")
        column = ColumnSelectorComponent()
        table = TableSelectorComponent(columns=[column])

        def go_add():
            # column.set(int(column) + 1)

            # todo: database type coercsion/detection?
            column << int(column) + 1

        ColumnXProductProcessor(columns=[column], func=go_add)
        show_results([column])
    tool.add_stage("add_one", add_one)

    def add_one_v2():
        TextComponent("Also adds one to each element of selected column")
        table = TableSelectorComponent()
        column = create_column_selector_from_table_selector(table)

        def do_add():
            print(int(column) + 1)
        ColumnXProductProcessor(columns=[column], func=do_add)
    tool.add_stage('add_one_v2', add_one_v2)

    def table_selector_stage():
        TextComponent("Pick a table:")
        table = TableSelectorComponent()
        show_results(table, label="Selected table:")
    tool.add_stage('table_selector', table_selector_stage)

    tool.run()


if __name__ == '__main__':
    main()
