from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage import config


class SubmitComponent(Component):
    """
    A component used to submit the form which comprises a stage's Config
    Renders as a submit button
    """
    def __init__(self, submit_text: str = ""):
        """
        Initialize this SubmitComponent
        Set config.submit_component_added to true so that we know not to
        procedurally add one to the Config when all the other components are
        finished being rendered
        :param submit_text:     The text to show on the submit button
        """
        if not isinstance(submit_text, str):
            raise TypeError("Expected submit_text to be a string")
        self.submit_text = submit_text

        super().__init__()

        config.submit_component_added = True

    def paint(self) -> str:
        """
        Paint this Submit Button as a snippet of HTML
        Use an <input> since we assume this will be inside a <form>
        :return:
        """
        if self.submit_text != "":
            return f'<button type="submit">{self.submit_text}</button>'
        else:
            return '<button type="submit">Submit</button>'
