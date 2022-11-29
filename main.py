from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool('adder')

    def adder_stage():
        num_a = UserInputComponent(float, label="Enter a number:")
        num_b = UserInputComponent(float, label="Enter another number:")
        LambdaProcessor(lambda: print(num_a + num_b))

    tool.add_stage('add_stage', adder_stage)
    tool.run()


if __name__ == '__main__':
    main()
