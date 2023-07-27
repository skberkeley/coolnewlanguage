from unittest.mock import Mock, patch

import pytest

from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.row import Row


class TestCNLType:
    ROW = Mock(spec=Row)

    def test_cnl_type_happy_path(self):
        # Do
        cnl_type = CNLType(TestCNLType.ROW)

        # Check
        assert cnl_type._hls_backing_row == TestCNLType.ROW
        assert cnl_type._custom_fields == {}

    def test_cnl_type_backing_row_is_not_a_row(self):
        with pytest.raises(TypeError, match="Expected backing_row to be a Row"):
            CNLType(Mock())

    @pytest.fixture
    def cnl_type(self) -> CNLType:
        return CNLType(TestCNLType.ROW)

    def test_fields(self, cnl_type: CNLType):
        with pytest.raises(NotImplementedError):
            cnl_type.fields()

    def test_setattr_value_is_field(self, cnl_type: CNLType):
        # Setup
        # Mock a Field instance
        mock_field = Mock(spec=Field)

        # Do
        cnl_type.field = mock_field

        # Check
        # Check that the field was set in _custom_fields as expected
        assert 'field' in cnl_type._custom_fields
        assert cnl_type._custom_fields['field'] == mock_field

    def test_setattr_value_is_not_field_key_name_is_in_slots(self, cnl_type: CNLType):
        # Setup
        # Mock a value
        mock_value = Mock(spec=Row)

        # Do
        cnl_type._hls_backing_row = mock_value

        # Check
        # Check that _hls_backing_row was assigned to
        assert cnl_type._hls_backing_row == mock_value
        # Check that _custom_fields wasn't added to
        assert cnl_type._custom_fields == {}

    def test_setattr_value_is_not_field_key_name_not_in_slots(self, cnl_type: CNLType):
        # Do, Check
        with pytest.raises(AttributeError):
            cnl_type.field = Mock()
        # Check that _custom_fields wasn't added to
        assert cnl_type._custom_fields == {}

    def test_setattr_attempted_assignment_to_custom_fields(self, cnl_type: CNLType):
        # Do, Check
        match = "Cannot overwrite attribute _custom_fields. Use another attribute name instead"
        with pytest.raises(AttributeError, match=match):
            cnl_type._custom_fields = Mock()
        # Check that _custom_fields is unchanged
        assert cnl_type._custom_fields == {}

    def test_setattr_attempt_assignment_to_hls_backing_row_with_non_row_object(self, cnl_type: CNLType):
        with pytest.raises(
                TypeError,
                match="Expected value to be a Row when assigning to attribute '_hls_backing_row'"
        ):
            cnl_type._hls_backing_row = Mock()

    def test_getattr(self, cnl_type: CNLType):
        # Setup
        mock_field = Mock(spec=Field)
        cnl_type.field = mock_field

        # Do, Check
        assert cnl_type.field == mock_field
        with pytest.raises(AttributeError):
            _ = cnl_type.not_a_field

    A_FIELD = Mock(spec=Field)
    ANOTHER_FIELD = Mock(spec=Field)
    YET_ANOTHER_FIELD = Mock(spec=Field)

    class BabysFirstType(CNLType):
        def fields(self) -> None:
            self.a_field = TestCNLType.A_FIELD
            self.another_field = TestCNLType.ANOTHER_FIELD
            self.yet_another_field = TestCNLType.YET_ANOTHER_FIELD

    def test_hls_type_to_fields_happy_path(self):
        # Do
        field_dict = CNLType._hls_type_to_fields(TestCNLType.BabysFirstType)

        # Check
        assert field_dict == {
            'a_field': TestCNLType.A_FIELD,
            'another_field': TestCNLType.ANOTHER_FIELD,
            'yet_another_field': TestCNLType.YET_ANOTHER_FIELD
        }

    class BabysFirstBadType:
        pass

    def test_hls_type_to_fields_cnl_type_is_not_a_cnl_type_subclass(self):
        with pytest.raises(TypeError, match="Expected cnl_type to be a subclass of CNLType"):
            CNLType._hls_type_to_fields(TestCNLType.BabysFirstBadType)
