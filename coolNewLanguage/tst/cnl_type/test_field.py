from unittest.mock import Mock

import pytest

from coolNewLanguage.src.cnl_type.field import Field


class TestField:
    DATA_TYPE = Mock(spec=type)

    def test_field_happy_path(self):
        # Do
        field = Field(TestField.DATA_TYPE, True)

        # Check
        assert field.data_type == TestField.DATA_TYPE
        assert field.optional

    def test_field_data_type_is_not_a_type(self):
        with pytest.raises(TypeError, match="Expected data_type to be a type"):
            Field(Mock())

    def test_field_optional_is_not_a_bool(self):
        with pytest.raises(TypeError, match="Expected optional to be a bool"):
            Field(TestField.DATA_TYPE, Mock())
