from coolNewLanguage.src.component.component import Component


class TextComponent(Component):
    def __init__(self, text: str):
        if not isinstance(text, str):
            raise TypeError("Expected a string for this TextComponent")
        self.text = text

        super().__init__()

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        :return:
        """
        return f'<p>{self.text}</p>'

    def __str__(self):
        return self.text
