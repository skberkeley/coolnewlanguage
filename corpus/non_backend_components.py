import coolNewLanguage.src as hilt

tool = hilt.Tool('non_backend_components')

def user_input_component():
    """
    A stage to test how UserInputComponents take user input and cast them to expected types.
    To test, run once with 'correct' inputs, and then run again where the input to int_user_input cannot be cast to
    an integer, which should then throw a user-friendly exception.
    :return:
    """
    str_user_input = hilt.UserInputComponent(str, "Enter a string: ")

    int_user_input = hilt.UserInputComponent(int, "Enter an integer: ")

    if tool.user_input_received():
        hilt.results.show_results((str_user_input, "String user input:"), (int_user_input, "Int user input:"))

tool.add_stage('user_input_component', user_input_component)

def text_component():
    """
    A stage to demo a text_component. To test, run and verify that it shows "Hello World"
    :return:
    """
    hilt.TextComponent(text="Hello World")
tool.add_stage('text_component', text_component)

tool.run()
