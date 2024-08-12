import jinja2

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.exceptions.CNLError import raise_type_casting_error
from coolNewLanguage.src.stage import config


class SelectorComponent(InputComponent):
    """
    A component which captures input from a choice of radio buttons
    """
    def __init__(self, options, label: str = ""):
        if not all(isinstance(option, str) for option in options):
            raise TypeError("Expected options to be a list of strings")
        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        # assign these first so that we can paint if needed
        self.label = label if label != "" else "Select an option below: "
        self.options = options

        super().__init__(str)

        if config.building_template:
            return

        try:
            self.value = self.expected_type(self.value)
        except Exception as e:
            raise_type_casting_error(value=self.value, expected_type=self.expected_type, error=e)

    def paint(self) -> str:
        """
        Paint this SelectorComponent as a snippet of HTML
        :return:
        """
        # Load the jinja template
        template: jinja2.Template = config.tool_under_construction.jinja_environment.get_template(
            name=consts.SELECTOR_COMPONENT_TEMPLATE_FILENAME
        )
        # Render and return the template
        return template.render(label=self.label, component_id=self.component_id, options=self.options)