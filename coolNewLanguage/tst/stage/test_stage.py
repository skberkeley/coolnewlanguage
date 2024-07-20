import asyncio
import urllib.parse
from unittest.mock import Mock, patch, NonCallableMock, AsyncMock, MagicMock

import jinja2
import pytest
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage import config
from coolNewLanguage.src.stage.stage import Stage


class TestStage:
    STAGE_NAME = "The world"
    STAGE_FUNC = Mock()
    STAGE_URL = "the_world"

    def test_stage_happy_path(self):
        # Do
        stage = Stage(TestStage.STAGE_NAME, TestStage.STAGE_FUNC)

        # Check
        assert stage.name == TestStage.STAGE_NAME
        assert stage.stage_func == TestStage.STAGE_FUNC
        # Check url was quoted
        assert stage.url == urllib.parse.quote(TestStage.STAGE_NAME)

    def test_stage_name_is_not_a_string(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected name to be a string"):
            Stage(Mock(), TestStage.STAGE_FUNC)

    def test_stage_stage_func_is_not_callable(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected stage_func to be callable"):
            Stage(TestStage.STAGE_NAME, NonCallableMock())

    def test_stage_name_starts_with_underscore(self):
        # Do, Check
        with pytest.raises(ValueError, match="Stage names cannot begin with underscores"):
            Stage(f"_{TestStage.STAGE_NAME}", TestStage.STAGE_FUNC)

    @pytest.fixture
    @patch('urllib.parse.quote')
    def stage(self, mock_quote: Mock):
        mock_quote.return_value = TestStage.STAGE_URL
        return Stage(TestStage.STAGE_NAME, TestStage.STAGE_FUNC)

    @patch('aiohttp.web.Response')
    @patch.object(Stage, 'paint')
    def test_handle(self, mock_paint: Mock, mock_response: Mock, stage: Stage):
        # Setup
        mock_template = Mock(spec=str)
        mock_paint.return_value = mock_template
        mock_response_instance = Mock(spec=web.Response)
        mock_response.return_value = mock_response_instance

        # Do
        response = asyncio.run(stage.handle(Mock(spec=web.Request)))

        # Check
        mock_paint.assert_called()
        mock_response.assert_called_with(body=mock_template, content_type=consts.AIOHTTP_HTML)
        assert response == mock_response_instance

    @patch('coolNewLanguage.src.stage.stage.process')
    @patch('coolNewLanguage.src.stage.stage.SubmitComponent')
    def test_paint(self, mock_SubmitComponent: Mock, mock_process: Mock, stage: Stage):
        # Setup
        # Mock a list of components to paint later
        mock_component1 = Mock(spec=Component)
        mock_painted_component_1 = Mock(str)
        mock_component1.paint = Mock(return_value=mock_painted_component_1)
        mock_component2 = Mock(spec=Component)
        mock_painted_component_2 = Mock(str)
        mock_component2.paint = Mock(return_value=mock_painted_component_2)
        config.component_list = [mock_component1, mock_component2]
        # Mock the jinja template being returned
        mock_process.running_tool = Mock()
        mock_process.running_tool.jinja_environment = Mock()
        mock_template = Mock(spec=jinja2.Template)
        mock_template.render = Mock()
        mock_process.running_tool.jinja_environment.get_template = Mock(return_value=mock_template)

        # Do
        stage.paint()

        # Check
        # Check that the stage func was called
        TestStage.STAGE_FUNC.assert_called()
        # Check that a SubmitComponent was instantiated
        mock_SubmitComponent.assert_called_with("Submit")
        # Check that components' paints were called
        mock_component1.paint.assert_called()
        mock_component2.paint.assert_called()
        # Make sure config variables are reset to their old values
        assert config.tool_under_construction is None
        assert not config.building_template
        assert config.component_list == []
        # Make sure num components has been reset
        assert Component.num_components == 0
        # Make sure template render was called correctly
        mock_template.render.assert_called_with(
            stage_name=TestStage.STAGE_NAME,
            form_action=f'/{TestStage.STAGE_URL}/post',
            form_method='post',
            component_list=[mock_painted_component_1, mock_painted_component_2]
        )

    @pytest.fixture
    def mock_request(self) -> Mock:
        return Mock(spec=web.Request)

    @patch.object(web, 'Response')
    @patch('coolNewLanguage.src.stage.stage.process')
    def test_post_handler_results_is_set_happy_path(
            self,
            mock_process: MagicMock,
            mock_Response: Mock,
            stage: Stage,
            mock_request: Mock
    ):
        # Setup
        # Mock the mock request's post method
        mock_post = AsyncMock()
        mock_request.post = mock_post
        # Mock Stage.results_template
        mock_results_template = Mock(spec=str)
        Stage.results_template = mock_results_template
        # Mock web.Response return value
        mock_response_instance = Mock(spec=web.Response)
        mock_Response.return_value = mock_response_instance

        # Do
        response = asyncio.run(stage.post_handler(mock_request))

        # Check
        # Check post body is inspected
        mock_post.assert_called()
        # Check post body, handling_post, num_components are reset
        assert mock_process.post_body is None
        assert not mock_process.handling_post
        assert Component.num_components == 0
        # Check table changes were flushed
        mock_process.running_tool.tables._flush_changes.assert_called_once()
        # Check that Stage.results_template was reset to None
        assert Stage.results_template is None
        # Check that web.Response was called and returned
        mock_Response.assert_called_with(body=mock_results_template, content_type=consts.AIOHTTP_HTML)
        assert response == mock_response_instance

    @patch('coolNewLanguage.src.stage.stage.process')
    def test_post_handler_no_results_set_happy_path(self, mock_process: MagicMock, stage: Stage, mock_request: Mock):
        # Setup
        # Mock the mock request's post method
        mock_post = AsyncMock()
        mock_request.post = mock_post
        # Set Stage.results_template to None
        Stage.results_template = None

        # Do, Check
        with pytest.raises(web.HTTPFound) as e:
            asyncio.run(stage.post_handler(mock_request))

        # Check
        # Check post body is inspected
        mock_post.assert_called()
        # Check post body, handling_post, num_components are reset
        assert mock_process.post_body is None
        assert not mock_process.handling_post
        assert Component.num_components == 0
        # Check raised redirect's location
        assert e.value.location == '/'

    @patch.object(web, 'Response')
    @patch('coolNewLanguage.src.stage.stage.process')
    def test_post_handler_approvals_template_set_happy_path(
            self,
            mock_process: MagicMock,
            mock_Response: MagicMock,
            stage: Stage,
            mock_request: Mock
    ):
        # Setup
        # Mock Stage.approvals_template
        mock_approvals_template = Mock()
        Stage.approvals_template = mock_approvals_template
        # Mock web.Response return value
        mock_response_instance = Mock(spec=web.Response)
        mock_Response.return_value = mock_response_instance

        # Do, Check
        response = asyncio.run(stage.post_handler(Mock(spec=web.Request)))

        # Check
        # Check that Stage.approvals_template was reset to None
        assert Stage.approvals_template is None
        # Check that cached table changes were cleared
        mock_process.running_tool.tables._clear_changes.assert_called_once()
        # Check that web.Response was called and returned
        mock_Response.assert_called_with(body=mock_approvals_template, content_type=consts.AIOHTTP_HTML)
        assert response == mock_response_instance

    def test_post_handler_request_is_not_web_request(self, stage: Stage):
        # Do, Check
        with pytest.raises(TypeError, match="Expected request to be a web Request"):
            asyncio.run(stage.post_handler(Mock()))
