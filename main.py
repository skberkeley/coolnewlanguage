from coolNewLanguage.src.Tool import Tool
from coolNewLanguage.src.modules.TextModule import TextModule


def main():
    tool = Tool(
        TextModule("This is a text module"),
        TextModule("This is another text module"),
        tool_name="my_first_tool",
    )
    tool.render()
    tool.run()


if __name__ == "__main__":
    main()
