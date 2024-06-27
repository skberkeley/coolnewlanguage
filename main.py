from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import *

tool = Tool("cool_tool")

word = ""

def get_user_word():
    user_input = UserInputComponent(str, label="Enter a word")

    if tool.user_input_received():
        global word
        word = user_input.value
        results.show_results([results.Result(word, "We stored the word:")])

tool.add_stage('get_user_word', get_user_word)

def show_stored_word():
    global word
    if word == "":
        TextComponent("User input word hasn't been collected yet")
    else:
        TextComponent(f"The user word is: {word}")

tool.add_stage('show_stored_word', show_stored_word)

tool.run()