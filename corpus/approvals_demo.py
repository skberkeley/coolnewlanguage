from coolNewLanguage.src.approvals import approvals
from coolNewLanguage.src.component.text_component import TextComponent
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
                "Names",
                [["First Name", "Last Name", "Age"], ["Oski", "Bear", "43"], ["Carol", "Christ", "500"]],
                return_existing_table=False,
                overwrite_existing_table=True,
                get_user_approvals=True
            )

        created_table = LambdaProcessor(create_table).result
        approvals.get_user_approvals()
        results.show_results([results.Result(created_table, "Created table:")])

    tool.add_stage('table_results', approve_table_from_list_list)

    tool.run()


if __name__ == '__main__':
    main()
