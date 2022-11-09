from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.stage.config import Config
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.tool import Tool


def main():
    upload_stage = Stage(
        name='Upload Stage',
        config=Config([TextComponent("Hello World")], submit_text="Go back"),
        process=None,
        results=None
    )
    my_tool = Tool(tool_name='my_first_tool', stages=[upload_stage])
    my_tool.run()


if __name__ == '__main__':
    main()
