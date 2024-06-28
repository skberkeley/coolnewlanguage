from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import *

tool = Tool("cool_tool")

def get_user_word():
    user_input = UserInputComponent(str, label="Enter a word")

    def save_word():
        tool.state['word'] = user_input.value
        results.show_results([results.Result(tool.state['word'], "We stored the word:")])

    LambdaProcessor(save_word)

tool.add_stage('get_user_word', get_user_word)

def show_stored_word():
    if 'word' not in tool.state:
        TextComponent("User input word hasn't been collected yet")
    else:
        TextComponent(f"The user word is: {tool.state['word']}")

tool.add_stage('show_stored_word', show_stored_word)

tool.run()