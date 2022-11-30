from coolNewLanguage.src.component.input_component import InputComponent


class UserInputComponent(InputComponent):
    """
    An input component which captures some input which the user types
    """
    def __init__(self, expected_type: type, label: str = ""):
        # assign these first so that we can paint if needed
        if not isinstance(label, str):
            raise TypeError("label of a user input component should be a string")
        self.label = label

        super().__init__(expected_type)

    def paint(self) -> str:
        """
        Paint this UserInputComponent as a snippet of HTML
        :return:
        """
        snippets = ['<div>']

        # add label if necessary
        if self.label:
            snippets.append(
                f'<label for="{self.component_id}">{self.label}</label>'
            )
            snippets.append('<br>')

        # user input element
        snippets.append(
            f'<input type="text" id="{self.component_id}" name="{self.component_id}" />'
        )

        snippets.append('</div>')

        return ''.join(snippets)
