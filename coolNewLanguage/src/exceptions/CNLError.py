from typing import Any


class CNLError(Exception):
    def __init__(self, message, error: Exception):
        super().__init__(message)
        self.error = error


def raise_type_casting_error(value: Any, expected_type: type, error: Exception):
    raise CNLError(f"An error occurred while trying to cast {value} to {expected_type}", error)
