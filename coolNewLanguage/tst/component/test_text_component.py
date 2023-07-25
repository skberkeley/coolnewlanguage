from unittest.mock import Mock, patch

import pytest

import coolNewLanguage.src.component.component
from coolNewLanguage.src.component.text_component import TextComponent


class TestTextComponent:
    TEXT = "Deep insightful message"
    @patch.object(coolNewLanguage.src.component.component.Component, '__init__')
    def test_text_component_happy_path(self, mock_component_init: Mock):
        # Do
        text_component = TextComponent(TestTextComponent.TEXT)

        # Check
        assert text_component.text == TestTextComponent.TEXT
        mock_component_init.assert_called()

    def test_text_component_non_string_text(self):
        with pytest.raises(TypeError, match="Expected text to be a string"):
            TextComponent(Mock())

    @pytest.fixture
    @patch.object(coolNewLanguage.src.component.component.Component, '__init__')
    def text_component(self, _) -> TextComponent:
        return TextComponent(TestTextComponent.TEXT)

    def test_text_component_paint(self, text_component: TextComponent):
        # Do
        painted_text_component = text_component.paint()

        # Check
        assert painted_text_component == f'<p>{TestTextComponent.TEXT}</p>'
