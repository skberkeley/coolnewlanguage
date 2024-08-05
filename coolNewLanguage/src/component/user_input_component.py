import jinja2

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.exceptions.CNLError import raise_type_casting_error
from coolNewLanguage.src.stage import config


class UserInputComponent(InputComponent):
    """
    An input component which captures some input which the user types
    """
    def __init__(self, expected_type: type, label: str = ""):
        if not isinstance(expected_type, type):
            raise TypeError("Expected expected_type to be a type")
        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")
        # assign these first so that we can paint if needed
        self.label = label
        self.expected_type = expected_type

        super().__init__(expected_type)

        if self.value is None:
            return

        try:
            self.value = self.expected_type(self.value)
        except Exception as e:
            raise_type_casting_error(value=self.value, expected_type=self.expected_type, error=e)

    def paint(self) -> str:
        """
        Paint this UserInputComponent as a snippet of HTML
        :return:
        """
        # Load the jinja template
        template: jinja2.Template = config.tool_under_construction.jinja_environment.get_template(
            name=consts.USER_INPUT_COMPONENT_TEMPLATE_FILENAME
        )
        # Render and return the template
        return template.render(label=self.label, component_id=self.component_id)
