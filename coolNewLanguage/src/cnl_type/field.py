from typing import Any

from coolNewLanguage.src.exceptions.CNLError import raise_type_casting_error


class Field:
    """
    A field within a programmer-defined CNLType

    Attributes:
        data_type: The expected type of data that will live in this Field
        optional: Whether this Field is required for every instance of the host CNLType
        value: The actual value present in this field in a particular CNLType instance. Objects setting this value
            use the set_value method to ensure that values are properly type cast
    """
    __slots__ = ('data_type', 'optional', 'value')

    def __init__(self, data_type: type, optional: bool = False) -> None:
        if not isinstance(data_type, type):
            raise TypeError("Expected data_type to be a type")
        if not isinstance(optional, bool):
            raise TypeError("Expected optional to be a bool")

        self.data_type = data_type
        self.optional = optional
        self.value = None

    def set_value(self, value: Any) -> None:
        """
        Casts val to this field's data_type before setting its value.
        :param value:
        :return:
        """
        try:
            value = self.data_type(value)
        except Exception as e:
            raise_type_casting_error(value, self.data_type, e)
        self.value = value
