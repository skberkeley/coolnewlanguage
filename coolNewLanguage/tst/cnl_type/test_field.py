from unittest.mock import Mock

import pytest

from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.exceptions.CNLError import CNLError


class TestField:
    DATA_TYPE = Mock(spec=type)

    def test_field_happy_path(self):
        # Do
        field = Field(TestField.DATA_TYPE, True)

        # Check
        assert field.data_type == TestField.DATA_TYPE
        assert field.optional
        assert field.value is None

    def test_field_data_type_is_not_a_type(self):
        with pytest.raises(TypeError, match="Expected data_type to be a type"):
            Field(Mock())

    def test_field_optional_is_not_a_bool(self):
        with pytest.raises(TypeError, match="Expected optional to be a bool"):
            Field(TestField.DATA_TYPE, Mock())

    @pytest.fixture
    def field(self) -> Field:
        return Field(TestField.DATA_TYPE)

    def test_set_value_happy_path(self, field: Field):
        # Setup
        mock_val = Mock()
        TestField.DATA_TYPE.return_value = mock_val

        # Do
        field.set_value(mock_val)

        # Check
        # Check that mock_val was cast
        TestField.DATA_TYPE.assert_called_with(mock_val)
        # Check that field's value attribute was set
        assert field.value == mock_val

    def test_set_value_type_cast_fails(self, field: Field):
        TestField.DATA_TYPE.side_effect = Exception()
        with pytest.raises(CNLError):
            field.set_value(Mock())
        assert field.value is None
