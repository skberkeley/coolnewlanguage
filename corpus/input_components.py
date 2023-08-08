from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage.results import show_results, add_result
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool('input_components')

    def user_input_component():
        """
        A stage to test how UserInputComponents take user input and cast them to expected types.
        To test, run once with 'correct' inputs, and then run again where the input to int_user_input cannot be cast to
        an integer, which should then throw a user-friendly exception.
        :return:
        """
        str_user_input = UserInputComponent(str, "Enter a string: ")
        add_result(value=str_user_input, label="String user input:")

        int_user_input = UserInputComponent(int, "Enter an integer: ")
        add_result(value=int_user_input, label="Int user input:")

        show_results()
    tool.add_stage('user_input_component', user_input_component)

    tool.run()


if __name__ == '__main__':
    main()