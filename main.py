from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.tool import Tool


def main():
    text_stage = Stage(name='Text Stage', config=[TextComponent("Hello World")], process=None, results=None)
    my_tool = Tool(tool_name='my_first_tool', stages=[text_stage])
    my_tool.run()


if __name__ == '__main__':
    main()
