class Field:
    """
    A field within a programmer-defined CNLType

    Attributes:
        data_type: The expected type of data that will live in this Field
        optional: Whether this Field is required for every instance of the host CNLType
    """
    __slots__ = ('data_type', 'optional')

    def __init__(self, data_type: type, optional: bool = False) -> None:
        if not isinstance(data_type, type):
            raise TypeError("Expected data_type to be a type")
        if not isinstance(optional, bool):
            raise TypeError("Expected optional to be a bool")

        self.data_type = data_type
        self.optional = optional
