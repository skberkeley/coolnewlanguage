from unittest.mock import Mock, patch

import jinja2
import pytest

import coolNewLanguage.src.component.input_component
from coolNewLanguage.src import consts
from coolNewLanguage.src.component.user_input_component import UserInputComponent


class TestUserInputComponent:
    EXPECTED_TYPE = Mock(spec=type)
    LABEL = "Gimme input"
    COMPONENT_ID = "c o m p o n e n t"

    @patch.object(coolNewLanguage.src.component.input_component.InputComponent, '__init__')
    def test_user_input_component_happy_path(self, mock_input_component_init: Mock):
        # Do
        user_input_component = UserInputComponent(TestUserInputComponent.EXPECTED_TYPE, TestUserInputComponent.LABEL)

        # Check
        assert user_input_component.label == TestUserInputComponent.LABEL
        mock_input_component_init.assert_called_with(TestUserInputComponent.EXPECTED_TYPE)

    def test_user_input_component_expected_type_is_not_a_type(self):
        with pytest.raises(TypeError, match="Expected expected_type to be a type"):
            UserInputComponent(Mock())

    def test_user_input_component_label_is_not_a_string(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            UserInputComponent(TestUserInputComponent.EXPECTED_TYPE, Mock())

    def new_input_component_init(self, _: type):
        self.component_id = TestUserInputComponent.COMPONENT_ID

    @pytest.fixture
    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=new_input_component_init
    )
    def user_input_component(self):
        return UserInputComponent(TestUserInputComponent.EXPECTED_TYPE, TestUserInputComponent.LABEL)

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
            label=TestUserInputComponent.LABEL,
            component_id=TestUserInputComponent.COMPONENT_ID
        )
        assert painted_user_input_component == mock_rendered_template
