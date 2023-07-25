from unittest.mock import patch, Mock

import pytest

import coolNewLanguage.src.component.component
from coolNewLanguage.src.component.submit_component import SubmitComponent
from coolNewLanguage.src.stage import config


class TestSubmitComponent:
    SUBMIT_TEXT = "Submit me"

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        config.submit_component_added = False

        yield

        config.submit_component_added = False

    @patch.object(coolNewLanguage.src.component.component.Component, '__init__')
    def test_submit_component_happy_path(self, mock_component_init: Mock):
        # Do
        submit_component = SubmitComponent(TestSubmitComponent.SUBMIT_TEXT)

        # Check
        assert submit_component.submit_text == TestSubmitComponent.SUBMIT_TEXT
        mock_component_init.assert_called()
        assert config.submit_component_added

    def test_submit_component_non_string_submit_text(self):
        with pytest.raises(TypeError, match="Expected submit_text to be a string"):
            SubmitComponent(Mock())

    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=Mock())
    def test_submit_component_paint_non_empty_submit_text(self):
        # Setup
        submit_component = SubmitComponent(TestSubmitComponent.SUBMIT_TEXT)

        # Do
        painted_submit_component = submit_component.paint()

        # Check
        assert painted_submit_component == f'<input type="submit" value="{TestSubmitComponent.SUBMIT_TEXT}">'

    @patch.object(coolNewLanguage.src.component.component.Component, '__init__', new=Mock())
    def test_submit_component_paint_empty_submit_text(self):
        # Setup
        submit_component = SubmitComponent()

        # Do
        painted_submit_component = submit_component.paint()

        # Check
        assert painted_submit_component == f'<input type="submit">'
