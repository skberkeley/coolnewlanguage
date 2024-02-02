from coolNewLanguage.src.approvals import approvals
from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util import db_utils


def main():
    tool = Tool('approvals_demo')

    def approve_table_from_list_list():
        TextComponent("Creating and displaying a table to approve")

        def create_table():
            return db_utils.create_table_from_lists(
                "First Names",
                [["First Name"], ["Oski"], ["Carol"]],
                return_existing_table=False,
                overwrite_existing_table=True,
                get_user_approvals=True
            )

        created_table = LambdaProcessor(create_table).result
        approvals.get_user_approvals()
        results.show_results([results.Result(created_table, "Created table:")])

    tool.add_stage('table_results', approve_table_from_list_list)

    def approve_append_to_table():
        table = TableSelectorComponent(label="Select Names")

        def append_to_names():
            table.append({"First Name": "Steve", "Last Name": "Wozniak", "Age": "73"}, get_user_approvals=True)

        LambdaProcessor(append_to_names)
        approvals.get_user_approvals()
        results.show_results([results.Result(table, "Appended to table:")])

    tool.add_stage('append_to_table', approve_append_to_table)

    def approve_update_row_of_table():
        age_column = ColumnSelectorComponent(label="Select age Column", expected_val_types=[int])
        table = TableSelectorComponent(label="Select Names")

        def increment_age():
            for row in table:
                row[age_column] += 1
                row.save(get_user_approvals=True)

        LambdaProcessor(increment_age)
        approvals.get_user_approvals()
        results.show_results([results.Result(table, "Updated table:")])

    tool.add_stage('update_row_of_table', approve_update_row_of_table)

    class Person(CNLType):
        def fields(self) -> None:
            self.first_name = Field(data_type=str)
            self.last_name = Field(data_type=str)
            self.age = Field(data_type=int)

    def approve_update_table_via_CNLType():
        age_column = ColumnSelectorComponent(label="Select age Column", expected_val_type=int)
        table = TableSelectorComponent(label="Select Names", columns=[age_column])

        def update_table():
            for row in table:
                person = Person(row)
                person.set_field_column('age', age_column)
                person.age += 1
                person.save(get_user_approvals=True)

        LambdaProcessor(update_table)
        approvals.get_user_approvals()
        results.show_results([results.Result(table, "Updated table:")])

    tool.add_stage('update_table_via_CNLType', approve_update_table_via_CNLType)

    def approve_table_append_via_CNLType():
        first_name = UserInputComponent(str, label="First Name")
        last_name = UserInputComponent(str, label="Last Name")
        age = UserInputComponent(int, label="Age")
        first_name_column = ColumnSelectorComponent(label="Select first name Column")
        last_name_column = ColumnSelectorComponent(label="Select last name Column")
        age_column = ColumnSelectorComponent(label="Select age Column")
        table = TableSelectorComponent(label="Select Names", columns=[first_name_column, last_name_column, age_column])

        def append_to_table():
            person = Person()
            person.first_name = first_name
            person.set_field_column('first_name', first_name_column)
            person.last_name = last_name
            person.set_field_column('last_name', last_name_column)
            person.age = age
            person.set_field_column('age', age_column)
            table.append(person, get_user_approvals=True)

        LambdaProcessor(append_to_table)
        approvals.get_user_approvals()
        results.show_results([results.Result(table, "Appended to table:")])

    tool.add_stage('table_append_via_CNLType', approve_table_append_via_CNLType)

    same_person_link_metatype = tool.register_link_metatype("same person")

    def approve_row_links():
        first_name_column_1 = ColumnSelectorComponent(label="Select first name Column")
        names_table = TableSelectorComponent(label="Select Names", columns=[first_name_column_1])
        first_name_column_2 = ColumnSelectorComponent(label="Select first name Column")
        first_name_table = TableSelectorComponent(label="Select First Names", columns=[first_name_column_2])

        def find_and_link():
            found_links = []
            for row in names_table:
                first_name = row[first_name_column_1]
                for row2 in first_name_table:
                    if row2[first_name_column_2] == first_name:
                        link = row.link(row2, link_metatype=same_person_link_metatype, get_user_approvals=True)
                        found_links.append(results.Result(link))
                        break
            return found_links

        found_link_results = LambdaProcessor(find_and_link).result
        approvals.get_user_approvals()
        results.show_results(found_link_results)

    tool.add_stage('row_links', approve_row_links)

    tool.run()


if __name__ == '__main__':
    main()
