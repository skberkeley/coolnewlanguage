from unittest.mock import Mock, patch, MagicMock

import pytest

from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.row import Row


class TestCNLType:
    ROW = MagicMock(spec=Row)
    A_FIELD = Mock(spec=Field)
    ANOTHER_FIELD = Mock(spec=Field)
    YET_ANOTHER_FIELD = Mock(spec=Field)

    class BabysFirstType(CNLType):
        def fields(self) -> None:
            self.a_field = TestCNLType.A_FIELD
            self.another_field = TestCNLType.ANOTHER_FIELD
            self.yet_another_field = TestCNLType.YET_ANOTHER_FIELD

    @pytest.fixture
    def babys_first_type(self):
        return TestCNLType.BabysFirstType(TestCNLType.ROW)

    class BabysFirstBadType:
        pass

    def test_cnl_type_happy_path(self):
        # Do
        cnl_type = CNLType(TestCNLType.ROW)

        # Check
        assert cnl_type._hls_backing_row == TestCNLType.ROW
        assert cnl_type._custom_fields == {}
        # Implicitly checks that field wasn't called, since if it was, a NotImplementedError would be raised

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

    def test_setattr_assignment_to_programmer_defined_attribute(self, babys_first_type):
        # Setup
        # Mock field's set_value
        TestCNLType.A_FIELD.set_value = Mock()
        mock_value = Mock()

        # Do
        babys_first_type.a_field = mock_value

        # Check
        # Check that the set_value was called as expected
        TestCNLType.A_FIELD.set_value.assert_called_with(mock_value)

    def test_getattr_custom_fields_field_object_has_value(self, babys_first_type):
        # Setup
        # Mock the field's value
        mock_value = Mock()
        babys_first_type._custom_fields['a_field'].value = mock_value

        # Do
        returned_value = babys_first_type.a_field

        # Check
        assert returned_value == mock_value

    def test_getattr_custom_fields_field_has_no_value_row_has_no_value(self):
        # Setup
        # Create a new BabysFirstType instance with no backing row
        babys_first_type = TestCNLType.BabysFirstType(backing_row=None)
        # Mock the field's value to be None
        babys_first_type._custom_fields['a_field'].value = None

        # Do
        returned_value = babys_first_type.a_field

        # Check
        assert returned_value is None

    def test_getattr_custom_fields_field_has_no_value_row_has_value(self, babys_first_type):
        # Setup
        # Mock the field's value to be None
        babys_first_type._custom_fields['a_field'].value = None
        # Mock the row mapping to behave like it contains the value
        TestCNLType.ROW.__contains__.return_value = True
        mock_value = Mock()
        TestCNLType.ROW.__getitem__.return_value = mock_value

        # Do
        returned_value = babys_first_type.a_field

        # Check
        assert returned_value == mock_value
        TestCNLType.ROW.__contains__.assert_called_with('a_field')
        TestCNLType.ROW.__getitem__.assert_called_with('a_field')
        # Check that the value was set on the Field instance's value attribute
        babys_first_type._custom_fields['a_field'].set_value.assert_called_with(mock_value)

    def test_getattr_custom_fields_field_has_no_value_value_not_in_row(self, babys_first_type):
        # Setup
        # Mock the field's value to be None
        babys_first_type._custom_fields['a_field'].value = None
        # Mock the row mapping to behave like it contains the value
        TestCNLType.ROW.__contains__.return_value = False

        # Do
        returned_value = babys_first_type.a_field

        # Check
        assert returned_value is None
        TestCNLType.ROW.__contains__.assert_called_with('a_field')

    def test_getattr_item_is_not_in_custom_fields(self, babys_first_type):
        with pytest.raises(AttributeError):
            _ = babys_first_type.not_a_field

    def test_cnl_type_subclass_init_happy_path(self):
        # Do
        babys_first_type = TestCNLType.BabysFirstType(TestCNLType.ROW)

        # Check
        assert babys_first_type._hls_backing_row == TestCNLType.ROW
        # Check that fields was called by checking the contents of _custom_fields
        assert babys_first_type._custom_fields == {
            'a_field': TestCNLType.A_FIELD,
            'another_field': TestCNLType.ANOTHER_FIELD,
            'yet_another_field': TestCNLType.YET_ANOTHER_FIELD
        }

    def test_hls_type_to_fields_happy_path(self):
        # Do
        field_dict = CNLType._hls_type_to_fields(TestCNLType.BabysFirstType)

        # Check
        assert field_dict == {
            'a_field': TestCNLType.A_FIELD,
            'another_field': TestCNLType.ANOTHER_FIELD,
            'yet_another_field': TestCNLType.YET_ANOTHER_FIELD
        }

    def test_hls_type_to_fields_cnl_type_is_not_a_cnl_type_subclass(self):
        with pytest.raises(TypeError, match="Expected cnl_type to be a subclass of CNLType"):
            CNLType._hls_type_to_fields(TestCNLType.BabysFirstBadType)
