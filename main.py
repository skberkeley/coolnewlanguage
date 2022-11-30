from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage.results import show_results
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool('adder')

    def adder_stage():
        num_a = UserInputComponent(float, label="Enter a number:")
        num_b = UserInputComponent(float, label="Enter another number:")
        processor = LambdaProcessor(lambda: num_a + num_b)
        result = processor.result
        show_results(result, label="Sum is: ")

    tool.add_stage('add_stage', adder_stage)
    tool.run()


if __name__ == '__main__':
    main()
