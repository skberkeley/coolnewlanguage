from coolNewLanguage.src.component.component import Component


class TextComponent(Component):
    """
    A component used to render some text within a Config
    """
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise TypeError("Expected text to be a string")
        self.text = text

        super().__init__()

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        :return:
        """
        return f'<p>{self.text}</p>'
