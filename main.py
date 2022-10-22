from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.page.page import Page
from coolNewLanguage.src.tool import Tool


def main():
    tool = Tool(
        "my_first_tool",
        Page(
            "my_first_tool home page",
            TextComponent("This is some text")
        ),
    )
    tool.run()


if __name__ == '__main__':
    main()
