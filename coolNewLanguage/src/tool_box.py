from coolNewLanguage.src.tool import Tool


class ToolBox:
    def __init__(self, *tools: Tool):
        if not all([isinstance(t, Tool) for t in tools]):
            raise TypeError("Everything in a ToolBox should be a Tool")

    def run(self):
        pass