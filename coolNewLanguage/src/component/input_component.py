from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage import process


class InputComponent(Component):
    """
    A component which is expected to take some kind of user input
    """

    def __init__(self, expected_type: type):
        """
        Initialize this input component
        If currently handling a post request, get the input value from
        the POST request's body
        :param expected_type: The expected type of the eventual user input
        """
        if not isinstance(expected_type, type):
            raise TypeError("Expected expected_type to be a type")

        super().__init__()

        self.expected_type = expected_type

        if process.handling_post:
            values = process.post_body.getall(self.component_id)
            self.value = values if len(values) > 1 else values[0]
        else:
            self.value = None

    def paint(self):
        """
        Render this component as a snippet of HTML. Not implemented for the
        abstract InputComponent class
        :return:
        """
        raise NotImplementedError

    def __str__(self):
        """
        Return this InputComponent's value by trying to cast it to a string
        :return:
        """
        if self.value is None:
            raise ValueError("value was None")

        return str(self.value)
    
    def __int__(self):
        """
        Return this InputComponent's value by trying to cast it to an int
        :return: The int value of this Inputcomponent
        """
        if self.value is None:
            raise ValueError("value was None")

        return int(self.value)

    def __add__(self, other):
        """
        Add the value of this InputComponent, to other, usually another InputComponent,
        by casting self.value to the expected type
        :param other: The object to add self.value to
                      If also an InputComponent, cast it to its own expected type
        :return:
        """
        if self.value is None:
            raise ValueError("Current value not available")

        if isinstance(other, InputComponent):
            return self.expected_type(self.value) + other.expected_type(other.value)

        return self.expected_type(self.value) + other

    def __eq__(self, other):
        if self.value is None:
            return self == other
        if isinstance(other, InputComponent):
            other = other.expected_type(other.value)
        return self.expected_type(self.value) == other
