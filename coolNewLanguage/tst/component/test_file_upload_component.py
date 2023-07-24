import io
import os.path
import pathlib
from unittest.mock import Mock, patch

import aiohttp.web_request
import jinja2
import pytest

import coolNewLanguage.src.component.input_component
from coolNewLanguage.src import consts
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent


class TestFileUploadComponent:
    FILE_CONTENTS = "I am a file"
    FILENAME = 'real_file.txt'
    EXPECTED_EXT = 'txt'
    LABEL = "gimme a file"
    COMPONENT_ID = "da real component"

    def mock_input_component_init(self, _: type):
        # Mock an IOBase instance to attach to the mocked FileField
        mock_file = Mock(
            spec=io.IOBase,
            read=Mock(return_value=bytes(TestFileUploadComponent.FILE_CONTENTS, 'utf-8')),
            close=Mock()
        )
        # Mock a FileField and attach it as self.value
        self.value = Mock(
            spec=aiohttp.web_request.FileField,
            filename=TestFileUploadComponent.FILENAME,
            file=mock_file
        )

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=mock_input_component_init
    )
    def test_file_upload_component_happy_path(self, tmp_path: pathlib.Path):
        # Setup
        # Mock FILES_DIR to be tmp_path
        consts.FILES_DIR = tmp_path

        # Do
        file_upload_component = FileUploadComponent(TestFileUploadComponent.EXPECTED_EXT, TestFileUploadComponent.LABEL)

        # Check
        # Check the component's fields
        assert file_upload_component.expected_ext == TestFileUploadComponent.EXPECTED_EXT
        assert file_upload_component.label == TestFileUploadComponent.LABEL
        # Check a file was created, with same contents as expected
        expected_file_path = tmp_path.joinpath(TestFileUploadComponent.FILENAME)
        assert os.path.exists(expected_file_path)
        with open(expected_file_path) as f:
            assert f.read() == TestFileUploadComponent.FILE_CONTENTS
        assert file_upload_component.value == expected_file_path

    def mock_input_component_init_none_value(self, _: type):
        self.value = None
        self.component_id = TestFileUploadComponent.COMPONENT_ID

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=mock_input_component_init_none_value
    )
    def test_file_upload_component_value_is_none(self, tmp_path: pathlib.Path):
        # Setup
        # Mock FILES_DIR to be tmp_path
        consts.FILES_DIR = tmp_path

        # Do
        file_upload_component = FileUploadComponent(TestFileUploadComponent.EXPECTED_EXT, TestFileUploadComponent.LABEL)

        # Check
        # Check the component's fields
        assert file_upload_component.expected_ext == TestFileUploadComponent.EXPECTED_EXT
        assert file_upload_component.label == TestFileUploadComponent.LABEL
        # Check that the tmp_path dir is empty
        assert os.listdir(tmp_path) == []

    def test_file_upload_component_expected_ext_is_not_a_string(self):
        with pytest.raises(TypeError, match="Expected expected_ext to be a string"):
            FileUploadComponent(Mock(), TestFileUploadComponent.LABEL)

    def test_file_upload_component_label_is_not_a_string(self):
        with pytest.raises(TypeError, match="Expected label to be a string"):
            FileUploadComponent(TestFileUploadComponent.EXPECTED_EXT, Mock())

    def mock_input_component_init_non_aiohttp_file_field_value(self, _: type):
        self.value = Mock()

    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=mock_input_component_init_non_aiohttp_file_field_value
    )
    def test_file_upload_component_value_is_not_an_aiohttp_file_field(self):
        with pytest.raises(TypeError, match="Expected value to be an aiohttp FileField"):
            FileUploadComponent(TestFileUploadComponent.EXPECTED_EXT, TestFileUploadComponent.LABEL)

    @pytest.fixture
    @patch.object(
        coolNewLanguage.src.component.input_component.InputComponent,
        '__init__',
        new=mock_input_component_init_none_value
    )
    def file_upload_component(self):
        return FileUploadComponent(
            expected_ext=TestFileUploadComponent.EXPECTED_EXT,
            label=TestFileUploadComponent.LABEL
        )

    @patch('coolNewLanguage.src.stage.config.tool_under_construction')
    def test_paint_happy_path(self, mock_tool_under_construction: Mock, file_upload_component: FileUploadComponent):
        # Setup
        mock_rendered_template = Mock(spec=str)
        mock_template = Mock(spec=jinja2.Template, render=Mock(return_value=mock_rendered_template))
        mock_get_template = Mock(return_value=mock_template)
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_tool_under_construction.jinja_environment = mock_jinja_environment

        # Do
        painted_file_upload_component = file_upload_component.paint()

        # Check
        mock_get_template.assert_called_with(name=consts.FILE_UPLOAD_COMPONENT_TEMPLATE_FILENAME)
        mock_template.render.assert_called_with(
            label=TestFileUploadComponent.LABEL,
            component_id=TestFileUploadComponent.COMPONENT_ID,
            expected_ext=TestFileUploadComponent.EXPECTED_EXT
        )
        assert painted_file_upload_component == mock_rendered_template
