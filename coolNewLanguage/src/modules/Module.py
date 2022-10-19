from coolNewLanguage.src.Tool import Tool


class Module:
    def __init__(self):
        self._rendered = False
        self._tool = None

    @property
    def rendered(self) -> bool:
        """Whether django files have been modified to show this module"""
        return self._rendered

    @rendered.setter
    def rendered(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(value, "rendered should be set to a bool")
        self._rendered = value

    def render(self):
        """
        Modify
        :return:
        """
        self.rendered = True

    @property
    def tool(self) -> Tool:
        """The tool which this module is a part of"""
        return self._tool

    @tool.setter
    def tool(self, value: Tool):
        if not isinstance(value, Tool):
            raise TypeError(value, "tool should be set to a Tool")
        self._tool = value
