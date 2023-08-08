from unittest.mock import Mock, patch

import jinja2
import pytest

import coolNewLanguage.src.component.input_component
from coolNewLanguage.src import consts
from coolNewLanguage.src.component.user_input_component import UserInputComponent


class TestUserInputComponent:
    LABEL = "Gimme input"
    COMPONENT_ID = "c o m p o n e n t"
    MOCK_VALUE = Mock()

    @pytest.fixture
    def mock_expected_type(self):
        return Mock(spec=type)

    def new_input_component_init(self, expected_type: type):
        self.component_id = TestUserInputComponent.COMPONENT_ID
        self.value = TestUserInputComponent.MOCK_VALUE
        self.expected_type = expected_type

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    def test_user_input_component_happy_path(self, mock_expected_type: Mock):
        # Setup
        # Mock type casting result
        mock_type_cast_result = Mock()
        mock_expected_type.return_value = mock_type_cast_result

        # Do
        user_input_component = UserInputComponent(mock_expected_type, self.LABEL)

        # Check
        assert user_input_component.label == self.LABEL
        # Check that value was cast and re-set
        mock_expected_type.assert_called_with(self.MOCK_VALUE)
        assert user_input_component.value == mock_type_cast_result

    def test_user_input_component_expected_type_is_not_a_type(self):
        with pytest.raises(TypeError, match="Expected expected_type to be a type"):
            UserInputComponent(Mock())

    def test_user_input_component_label_is_not_a_string(self, mock_expected_type: Mock):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            UserInputComponent(mock_expected_type, Mock())

    def new_input_component_init_value_is_none(self, _):
        self.value = None

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init_value_is_none
    )
    def test_user_input_component_no_value(self, mock_expected_type: Mock):
        # Do
        user_input_component = UserInputComponent(mock_expected_type, self.LABEL)

        # Check
        assert user_input_component.label == self.LABEL
        # Check that no type cast was attempted
        mock_expected_type.assert_not_called()

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    @patch('coolNewLanguage.src.component.user_input_component.raise_type_casting_error')
    def test_user_input_component_type_cast_fails(self, mock_raise_type_casting_error: Mock, mock_expected_type: Mock):
        # Setup
        # Make type cast fail
        mock_expected_type.side_effect = Exception()

        # Do
        user_input_component = UserInputComponent(mock_expected_type, self.LABEL)

        # Check
        assert user_input_component.label == self.LABEL
        # Check that raise_type_casting_error was called
        mock_raise_type_casting_error.assert_called()

    @pytest.fixture
    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    def user_input_component(self, mock_expected_type: Mock):
        return UserInputComponent(mock_expected_type, self.LABEL)

    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_paint_happy_path(self, mock_tool_under_construction: Mock, user_input_component: UserInputComponent):
        # Setup
        mock_rendered_template = Mock(spec=str)
        mock_template = Mock(spec=jinja2.Template, render=Mock(return_value=mock_rendered_template))
        mock_get_template = Mock(return_value=mock_template)
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_tool_under_construction.jinja_environment = mock_jinja_environment

        # Do
        painted_user_input_component = user_input_component.paint()

        # Check
        mock_get_template.assert_called_with(name=consts.USER_INPUT_COMPONENT_TEMPLATE_FILENAME)
        mock_template.render.assert_called_with(
            label=self.LABEL,
            component_id=self.COMPONENT_ID
        )
        assert painted_user_input_component == mock_rendered_template
