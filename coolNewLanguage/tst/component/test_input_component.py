from unittest.mock import Mock, patch

import pytest

import coolNewLanguage.src.component.component
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.stage import process


class TestInputComponent:
    COMPONENT_ID = 'component_0'
    VALUE = "YAHAHA"
    INT_VALUE = 1
    EXPECTED_TYPE = Mock(spec=type)


    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        process.handling_post = False

        yield

        process.handling_post = False
        process.post_body = None

    def mock_component_init(self):
        self.component_id = TestInputComponent.COMPONENT_ID

    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=mock_component_init)
    def test_input_component_handling_post_happy_path(self):
        # Setup
        process.post_body = {TestInputComponent.COMPONENT_ID: TestInputComponent.VALUE}
        process.handling_post = True

        # Do
        input_component = InputComponent(TestInputComponent.EXPECTED_TYPE)

        # Check
        assert input_component.expected_type == TestInputComponent.EXPECTED_TYPE
        assert input_component.value == TestInputComponent.VALUE

    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=mock_component_init)
    def test_input_component_not_handling_post_happy_path(self):
        # Setup
        process.handling_post = False

        # Do
        input_component = InputComponent(TestInputComponent.EXPECTED_TYPE)

        # Check
        assert input_component.expected_type == TestInputComponent.EXPECTED_TYPE
        assert input_component.value is None

    def test_input_component_expected_type_not_a_type(self):
        with pytest.raises(TypeError, match="Expected expected_type to be a type"):
            InputComponent(Mock())

    @pytest.fixture
    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=mock_component_init)
    def input_component_with_value(self):
        process.post_body = {TestInputComponent.COMPONENT_ID: TestInputComponent.VALUE}
        process.handling_post = True
        return InputComponent(TestInputComponent.EXPECTED_TYPE)

    @pytest.fixture
    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=mock_component_init)
    def input_component_without_value(self):
        return InputComponent(TestInputComponent.EXPECTED_TYPE)

    def test_input_component_paint(self, input_component_with_value: InputComponent):
        with pytest.raises(NotImplementedError):
            input_component_with_value.paint()

    def test_input_component_str_happy_path(self, input_component_with_value: InputComponent):
        assert str(input_component_with_value) == TestInputComponent.VALUE

    def test_input_component_str_value_is_none(self, input_component_without_value: InputComponent):
        with pytest.raises(ValueError, match="value was None"):
            str(input_component_without_value)

    @pytest.fixture
    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=mock_component_init)
    def input_component_with_int_value(self):
        process.post_body = {TestInputComponent.COMPONENT_ID: TestInputComponent.INT_VALUE}
        process.handling_post = True
        return InputComponent(TestInputComponent.EXPECTED_TYPE)

    def test_input_component_int_happy_path(self, input_component_with_int_value: InputComponent):
        assert int(input_component_with_int_value) == TestInputComponent.INT_VALUE

    def test_input_component_int_value_is_none(self, input_component_without_value):
        with pytest.raises(ValueError, match="value was None"):
            int(input_component_without_value)
