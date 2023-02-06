from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage.config import Config


class SubmitComponent(Component):
    """
    A component used to submit the form which comprises a stage's Config
    Renders as a submit button
    """
    def __init__(self, submit_text: str = ""):
        """
        Initialize this SubmitComponent
        Set Config.submit_component_added to true so that we know not to
        procedurally add one to the Config when all the other components are
        finished being rendered
        :param submit_text:     The text to show on the submit button
        """
        if not isinstance(submit_text, str):
            raise TypeError("submit text of a SubmitComponent should be a string")
        self.submit_text = submit_text

        super().__init__()

        Config.submit_component_added = True

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
