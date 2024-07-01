from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool('non_backend_components')

    def user_input_component():
        """
        A stage to test how UserInputComponents take user input and cast them to expected types.
        To test, run once with 'correct' inputs, and then run again where the input to int_user_input cannot be cast to
        an integer, which should then throw a user-friendly exception.
        :return:
        """
        str_user_input = UserInputComponent(str, "Enter a string: ")

        int_user_input = UserInputComponent(int, "Enter an integer: ")

        results.show_results((str_user_input, "String user input:"), (int_user_input, "Int user input:"))

    tool.add_stage('user_input_component', user_input_component)

    def text_component():
        """
        A stage to demo a text_component. To test, run and verify that it shows "Hello World"
        :return:
        """
        TextComponent(text="Hello World")
    tool.add_stage('text_component', text_component)

    tool.run()


if __name__ == '__main__':
    main()
