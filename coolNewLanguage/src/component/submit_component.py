from coolNewLanguage.src.component.component import Component


class SubmitComponent(Component):
    def __init__(self, submit_text: str = ""):
        if not isinstance(submit_text, str):
            raise TypeError("submit text of a SubmitComponent should be a string")
        self.submit_text = submit_text

    def paint(self) -> str:
        """
        Paint this Submit Button as a snippet of HTML
        Use an <input> since we assume this will be inside a <form>
        :return:
        """
        if self.submit_text:
            return f'<input type="submit" value="{self.submit_text}">'
        else:
            return '<input type="submit">'
