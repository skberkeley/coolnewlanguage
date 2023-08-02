from unittest.mock import patch, Mock

import pytest

from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.stage import process


class TestLink:
    LINK_NAME = "Zelda"
    LINK_META_ID = 4

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        process.handling_post = False

        yield

        process.handling_post = True

    @patch('coolNewLanguage.src.cnl_type.link.link_register')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_registration_id')
    def test_link_process_is_not_running(
            self,
            mock_get_link_registration_id: Mock,
            mock_link_register: Mock
    ):
        # Setup
        process.handling_post = False

        # Do
        link = Link(TestLink.LINK_NAME)

        # Check
        # Check that get_link_registration_id wasn't called
        mock_get_link_registration_id.assert_not_called()
        # Check that link_register wasn't called
        mock_link_register.assert_not_called()
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id is None

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.link_register')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_registration_id')
    def test_link_link_registration_already_exists_happy_path(
            self,
            mock_get_link_registration_id: Mock,
            mock_link_register: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        process.handling_post = True
        mock_get_link_registration_id.return_value = TestLink.LINK_META_ID

        # Do
        link = Link(TestLink.LINK_NAME)

        # Check
        # Check that get_link_registration_id was called
        mock_get_link_registration_id.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that link_register wasn't called
        mock_link_register.assert_not_called()
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id == TestLink.LINK_META_ID

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.link_register')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_registration_id')
    def test_link_link_registration_does_not_exist_happy_path(
            self,
            mock_get_link_registration_id: Mock,
            mock_link_register: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        process.handling_post = True
        mock_get_link_registration_id.return_value = None
        mock_link_register.return_value = TestLink.LINK_META_ID

        link = Link(TestLink.LINK_NAME)

        # Check
        # Check that get_link_registration_id was called
        mock_get_link_registration_id.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that link_register was called
        mock_link_register.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id == TestLink.LINK_META_ID

    def test_link_name_is_not_a_string(self):
        with pytest.raises(TypeError, match="Expected name to be a string"):
            Link(Mock())
