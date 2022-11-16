from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool('adder')

    def adder_stage():
        user_input = UserInputComponent(str, label="Enter something:")
        LambdaProcessor(lambda: print(user_input))

    tool.add_stage('add_stage', adder_stage)
    tool.run()


if __name__ == '__main__':
    main()
