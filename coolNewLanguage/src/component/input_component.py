from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.processor.processor import Processor


class InputComponent(Component):
    def __init__(self, expected_type: type):
        super().__init__()

        if not isinstance(expected_type, type):
            raise TypeError("expected type of an input component should be a type")
        self.expected_type = expected_type

        if Processor.run_process:
            self.value = Processor.post_body[self.component_id]
        else:
            self.value = None

    def __str__(self):
        if self.value is None:
            raise ValueError("Current value not available")

        return str(self.value)

    def __add__(self, other):
        if self.value is None:
            raise ValueError("Current value not available")

        if isinstance(other, InputComponent):
            return self.expected_type(self.value) + other.expected_type(other.value)

        return self.expected_type(self.value) + other
