from unittest.mock import patch, Mock

import pytest

from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype
from coolNewLanguage.src.stage import process


class TestLink:
    LINK_NAME = "Zelda"
    LINK_META_ID = 4

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        process.handling_post = False

        yield

        process.handling_post = True

    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_link_process_is_not_running(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock
    ):
        # Setup
        process.handling_post = False

        # Do
        link = LinkMetatype(TestLink.LINK_NAME)

        # Check
        # Check that get_link_metatype_id_from_metaname wasn't called
        mock_get_link_metatype_id_from_metaname.assert_not_called()
        # Check that register_link_metatype wasn't called
        mock_register_link_metatype.assert_not_called()
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id is None

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_link_link_registration_already_exists_happy_path(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        process.handling_post = True
        mock_get_link_metatype_id_from_metaname.return_value = TestLink.LINK_META_ID

        # Do
        link = LinkMetatype(TestLink.LINK_NAME)

        # Check
        # Check that get_link_metatype_id_from_metaname was called
        mock_get_link_metatype_id_from_metaname.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that register_link_metatype wasn't called
        mock_register_link_metatype.assert_not_called()
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id == TestLink.LINK_META_ID

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_link_link_registration_does_not_exist_happy_path(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            mock_running_tool: Mock
    ):
        # Setup
        process.handling_post = True
        mock_get_link_metatype_id_from_metaname.return_value = None
        mock_register_link_metatype.return_value = TestLink.LINK_META_ID

        link = LinkMetatype(TestLink.LINK_NAME)

        # Check
        # Check that get_link_metatype_id_from_metaname was called
        mock_get_link_metatype_id_from_metaname.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that register_link_metatype was called
        mock_register_link_metatype.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check link's fields
        assert link.meta_name == TestLink.LINK_NAME
        assert link._hls_internal_link_meta_id == TestLink.LINK_META_ID

    def test_link_name_is_not_a_string(self):
        with pytest.raises(TypeError, match="Expected name to be a string"):
            LinkMetatype(Mock())

    @pytest.fixture
    def link_with_no_meta_id(self) -> LinkMetatype:
        return LinkMetatype(TestLink.LINK_NAME)

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_get_link_meta_id_meta_id_is_none_handling_post_registration_exists(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            mock_running_tool: Mock,
            link_with_no_meta_id: LinkMetatype
    ):
        # Setup
        process.handling_post = True
        mock_get_link_metatype_id_from_metaname.return_value = TestLink.LINK_META_ID

        # Do
        meta_id = link_with_no_meta_id.get_link_meta_id()

        # Check
        # Check that get_link_metatype_id_from_metaname was called
        mock_get_link_metatype_id_from_metaname.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that register_link_metatype wasn't called
        mock_register_link_metatype.assert_not_called()
        # Check the returned meta_id
        assert meta_id == TestLink.LINK_META_ID

    @patch('coolNewLanguage.src.stage.process.running_tool')
    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_get_link_meta_id_meta_id_is_none_handling_post_registration_does_not_exist(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            mock_running_tool: Mock,
            link_with_no_meta_id: LinkMetatype
    ):
        # Setup
        process.handling_post = True
        mock_get_link_metatype_id_from_metaname.return_value = None
        mock_register_link_metatype.return_value = TestLink.LINK_META_ID

        # Do
        meta_id = link_with_no_meta_id.get_link_meta_id()

        # Check
        # Check that get_link_metatype_id_from_metaname was called
        mock_get_link_metatype_id_from_metaname.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check that register_link_metatype was called
        mock_register_link_metatype.assert_called_with(tool=mock_running_tool, link_meta_name=TestLink.LINK_NAME)
        # Check the returned meta_id
        assert meta_id == TestLink.LINK_META_ID

    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_get_link_meta_id_meta_id_is_none_not_handling_post(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            link_with_no_meta_id: LinkMetatype
    ):
        # Do
        meta_id = link_with_no_meta_id.get_link_meta_id()

        # Check
        # Check that get_link_metatype_id_from_metaname wasn't called
        mock_get_link_metatype_id_from_metaname.assert_not_called()
        # Check that register_link_metatype wasn't called
        mock_register_link_metatype.assert_not_called()
        # Check the returned meta_id
        assert meta_id is None

    @patch('coolNewLanguage.src.cnl_type.link.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.cnl_type.link.get_link_metatype_id_from_metaname')
    def test_get_link_meta_id_meta_id_is_not_none(
            self,
            mock_get_link_metatype_id_from_metaname: Mock,
            mock_register_link_metatype: Mock,
            link_with_no_meta_id: LinkMetatype
    ):
        # Setup
        link_with_no_meta_id._hls_internal_link_meta_id = TestLink.LINK_META_ID

        # Do
        meta_id = link_with_no_meta_id.get_link_meta_id()

        # Check
        # Check that get_link_metatype_id_from_metaname wasn't called
        mock_get_link_metatype_id_from_metaname.assert_not_called()
        # Check that register_link_metatype wasn't called
        mock_register_link_metatype.assert_not_called()
        # Check the returned meta_id
        assert meta_id == TestLink.LINK_META_ID
