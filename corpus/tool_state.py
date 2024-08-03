import coolNewLanguage.src as hilt

tool = hilt.Tool("cool_tool")

def get_user_word():
    user_input = hilt.UserInputComponent(str, label="Enter a word")

    if tool.user_input_received():
        tool.state['word'] = user_input.value

        hilt.results.show_results(hilt.results.Result(tool.state['word'], "We stored the word:"))

tool.add_stage('get_user_word', get_user_word)

def show_stored_word():
    if 'word' not in tool.state:
        hilt.TextComponent("User input word hasn't been collected yet")
    else:
        hilt.TextComponent(f"The user word is: {tool.state['word']}")

tool.add_stage('show_stored_word', show_stored_word)

tool.run()