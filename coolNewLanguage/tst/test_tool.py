import asyncio
import os.path
import pathlib
from unittest.mock import patch, Mock, NonCallableMock, call, MagicMock

import pytest
import sqlalchemy
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.consts import TEMPLATES_DIR, LANDING_PAGE_TEMPLATE_FILENAME,\
from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype
from coolNewLanguage.src.consts import TEMPLATES_DIR, LANDING_PAGE_TEMPLATE_FILENAME,\
    LANDING_PAGE_STAGES
from coolNewLanguage.src.stage import process
import coolNewLanguage.src.tool as toolModule
Tool = toolModule.Tool
from coolNewLanguage.src.web_app import WebApp


class TestTool:
    TOOL_NAME = "OSKI_TOOL"
    TOOL_URL = "OSKI"
    STAGE_NAME = "The Wizard of Woz"
    STAGE_FUNC = Mock()
    STAGE_URL = "the_wizard_of_woz"
    FILE_DIR_PATH = "a/real/path"

    @patch('coolNewLanguage.src.tool.tables')
    @patch('aiohttp_jinja2.setup')
    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    @patch.object(WebApp, 'add_static_file_handler')
    def test_tool_happy_path(self,
                             mock_add_static_file_handler: Mock,
                             mock_FileSystemLoader: Mock,
                             mock_Environment: Mock,
                             mock_aiohttp_jinja2_setup: Mock,
                             mock_tables_module: Mock,
                             tmp_path: pathlib.Path,
                             monkeypatch):
        # Setup
        mock_file_system_loader = mock_FileSystemLoader.return_value
        mock_environment = mock_Environment.return_value
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)
        # Monkey patch the db_awaken method so that it doesn't actually do anything
        mock_db_awaken = Mock()
        monkeypatch.setattr('coolNewLanguage.src.tool.Tool.db_awaken', mock_db_awaken)
        # Mock the Tables class
        mock_tables = Mock()
        mock_tables_module.Tables = Mock(return_value=mock_tables)

        # Do
        tool = Tool(tool_name=TestTool.TOOL_NAME, url=TestTool.TOOL_URL)

        # Check
        # tool name same
        assert tool.tool_name == TestTool.TOOL_NAME
        # stages empty
        assert len(tool.stages) == 0
        # url is same
        assert tool.url == TestTool.TOOL_URL
        # tool has a web app
        assert isinstance(tool.web_app, WebApp)
        # web app's add static file handler method was called
        mock_add_static_file_handler.assert_has_calls(
            [
                call(consts.STATIC_ROUTE, str(consts.STATIC_FILE_DIR)),
                call(consts.STYLES_ROUTE, str(consts.STYLES_DIR))
            ],
            any_order=True
        )
        # loader was created with templates dir
        mock_FileSystemLoader.assert_called_with(TEMPLATES_DIR)
        # jinja environment was created with loader
        mock_Environment.assert_called_with(loader=mock_file_system_loader)
        assert tool.jinja_environment is mock_environment
        # aiohttp jinja setup was called appropriately
        mock_aiohttp_jinja2_setup.assert_called_with(tool.web_app.app, loader=mock_file_system_loader)
        # data directory exists
        assert os.path.exists(tmp_path)
        # db engine was created
        assert isinstance(tool.db_engine, sqlalchemy.Engine)
        # sqlite file was created
        expected_db_path = tmp_path.joinpath(f'{TestTool.TOOL_URL}.db')
        assert os.path.exists(expected_db_path)
        # metadata obj was created
        assert isinstance(tool.db_metadata_obj, sqlalchemy.MetaData)
        # db_awaken was called
        mock_db_awaken.assert_called_with()
        # file_dir was set correctly
        expected_file_dir = consts.FILES_DIR.joinpath(TestTool.TOOL_NAME)
        assert tool.file_dir == expected_file_dir
        # file_dir exists
        assert os.path.exists(expected_file_dir)
        # tool has an empty state dictionary
        assert tool.state == {}
        # tool has a Tables instance
        assert tool.tables is mock_tables
        mock_tables_module.Tables.assert_called_with(tool)

    @patch.object(WebApp, 'add_static_file_handler')
    @patch('aiohttp_jinja2.setup')
    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    def test_tool_no_url_happy_path(
            self,
            mock_FileSystemLoader: Mock,
            mock_Environment: Mock,
            mock_aiohttp_jinja2_setup: Mock,
            mock_add_static_file_handler: Mock,
            tmp_path: pathlib.Path,
            monkeypatch
    ):
        # Setup
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)
        monkeypatch.setattr('coolNewLanguage.src.tool.STATIC_FILE_DIR', tmp_path)

        # Do
        tool = Tool(tool_name=TestTool.TOOL_NAME)

        # Check
        assert tool.url == TestTool.TOOL_NAME
        expected_db_path = tmp_path.joinpath(f'{TestTool.TOOL_NAME}.db')
        assert os.path.exists(expected_db_path)

    def test_tool_non_string_tool_name(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected a string for Tool name"):
            Tool(tool_name=Mock(), url=TestTool.TOOL_URL)

    def test_tool_non_string_url(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected a string for Tool url"):
            Tool(tool_name=TestTool.TOOL_NAME, url=Mock())

    def test_tool_invalid_tool_name(self):
        # Do, Check
        with pytest.raises(ValueError, match="Tool name can only contain alphanumeric characters and underscores"):
            Tool(tool_name="tool name with forbidden characters!", url=TestTool.TOOL_URL)

    def test_tool_invalid_url(self):
        # Do, Check
        with pytest.raises(ValueError, match="Tool url can only contain alphanumeric characters and underscores"):
            Tool(tool_name=TestTool.TOOL_NAME, url='not a      v a l i d      url')

    @patch.object(WebApp, 'add_static_file_handler')
    @patch('aiohttp_jinja2.setup')
    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    def test_tool_custom_file_dir_path(
            self,
            mock_FileSystemLoader: Mock,
            mock_Environment: Mock,
            mock_aiohttp_jinja2_setup: Mock,
            mock_add_static_file_handler: Mock,
            tmp_path: pathlib.Path,
            monkeypatch
    ):
        # Setup
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)
        monkeypatch.setattr('coolNewLanguage.src.tool.STATIC_FILE_DIR', tmp_path)

        # Do
        tool = Tool(tool_name=TestTool.TOOL_NAME, file_dir_path=TestTool.FILE_DIR_PATH)

        # Check
        expected_file_dir = pathlib.Path(TestTool.FILE_DIR_PATH)
        assert expected_file_dir == tool.file_dir

    def test_tool_non_string_file_dir_path(self):
        # Do, Check
        with pytest.raises(TypeError, match="Expected file_dir_path to be a string"):
            Tool(tool_name=TestTool.TOOL_NAME, file_dir_path=Mock())


    @pytest.fixture
    @patch('coolNewLanguage.src.tool.tables')
    @patch.object(WebApp, 'add_static_file_handler')
    def tool(self, mock_add_static_file_handler: Mock, mock_tables_module: Mock, tmp_path: pathlib.Path, monkeypatch) -> Tool:
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)
        monkeypatch.setattr('coolNewLanguage.src.tool.STATIC_FILE_DIR', tmp_path)

        mock_tables_module.Tables = Mock(return_value=MagicMock())

        return Tool(tool_name=TestTool.TOOL_NAME, url=TestTool.TOOL_URL)

    @patch('coolNewLanguage.src.tool.Stage')
    def test_add_stage_happy_path(self, mock_Stage: Mock, tool: Tool):
        # Setup
        mock_stage = mock_Stage.return_value
        length_before = len(tool.stages)

        # Do
        tool.add_stage(TestTool.STAGE_NAME, TestTool.STAGE_FUNC)

        # Check
        mock_Stage.assert_called_with(TestTool.STAGE_NAME, TestTool.STAGE_FUNC)
        assert len(tool.stages) == length_before + 1
        assert tool.stages[-1] is mock_stage

    def test_add_stage_non_string_stage_name(self, tool: Tool):
        # Do, Check
        with pytest.raises(TypeError, match="Expected stage_name to be a string"):
            tool.add_stage(Mock(), TestTool.STAGE_FUNC)

    def test_add_stage_non_callable_stage_func(self, tool: Tool):
        # Do, Check
        with pytest.raises(TypeError, match="Expected stage_func to be callable"):
            tool.add_stage(TestTool.STAGE_NAME, NonCallableMock())

    @patch('coolNewLanguage.src.tool.web.run_app')
    @patch('aiohttp.web.Application.add_routes')
    def test_run(self, mock_add_routes: Mock, mock_run_app: Mock, tool: Tool):
        # Setup
        # Add a Mock stage to the tool
        mock_stage = Mock(url=TestTool.STAGE_URL)
        tool.stages.append(mock_stage)
        # Prepare to mock the approvals module
        mock_approval_handler = Mock()
        mock_approvals = Mock()
        mock_approvals.approvals.approval_handler = mock_approval_handler

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.approvals': mock_approvals}):
            tool.run()

        # Check
        # Construct the table of expected routes
        # Landing page route, GET and POST routes for stage that was added
        routes = [
            web.get('/', tool.landing_page),
            web.get(consts.GET_TABLE_ROUTE, tool.get_table),
            web.get(f'/{TestTool.STAGE_URL}', mock_stage.handle),
            web.post(f'/{TestTool.STAGE_URL}/post', mock_stage.post_handler),
            web.post(f'/{TestTool.STAGE_URL}/approve', mock_approval_handler)
        ]
        # Check that add_routes was called with the expected routes
        mock_add_routes.assert_called_with(routes)
        # Check that tool has been assigned to process.running_tool
        assert process.running_tool is tool
        # Check that web.run_app was called appropriately
        mock_run_app.assert_called_with(tool.web_app.app, port=8000)

    def test_run_non_int_port(self, tool: Tool):
        # Do, Check
        with pytest.raises(TypeError, match="Expected port to be an int"):
            tool.run(port=Mock())

    @patch('aiohttp_jinja2.render_template')
    def test_landing_page_happy_path(self, mock_render_template: Mock, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)

        # Do
        asyncio.run(tool.landing_page(request))

        # Check
        mock_render_template.assert_called_with(
            template_name=LANDING_PAGE_TEMPLATE_FILENAME,
            request=request,
            context={LANDING_PAGE_STAGES: tool.stages}
        )

    def test_landing_page_non_web_request_request(self, tool: Tool):
        # Do, Check
        with pytest.raises(TypeError, match="Expected request to be an aiohttp web Request"):
            asyncio.run(tool.landing_page(Mock()))

    TABLE_NAME = 'cool_new_table'
    GET_TABLE_CONTEXT = 'get_table_context'
    COMPONENT_ID = 'component_id'
    TABLE_TRANSIENT_ID = 'table_transient_id'

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool, monkeypatch):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Monkeypatch get_table_from_table_name so that it returns a mock sqlalchemy table
        mock_sqlalchemy_table = Mock()
        mock_get_table_from_table_name = Mock(return_value=mock_sqlalchemy_table)
        monkeypatch.setattr(
            'coolNewLanguage.src.tool.Tool.get_table_from_table_name',
            mock_get_table_from_table_name
        )
        # Mock get_template behavior
        mock_jinja_template = Mock()
        mock_get_template = Mock(return_value=mock_jinja_template)
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Prepare to patch html_utils.html_of_table
        mock_template = Mock()
        mock_html_of_table = Mock(return_value=mock_template)
        mock_html_utils = Mock(html_of_table=mock_html_of_table)
        mock_utils = Mock(html_utils=mock_html_utils)
        # Mock web.Response
        mock_response_instance = Mock()
        mock_Response = Mock(return_value=mock_response_instance)
        mock_web.Response = mock_Response

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': mock_utils}):
            response = asyncio.run(tool.get_table(request))

        # Check
        # Check that get_table_from_table_name was called with the expected arguments
        mock_get_table_from_table_name.assert_called_with(TestTool.TABLE_NAME)
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.TABLE_RESULT_TEMPLATE_FILENAME)
        # Check that html_of_table was called with the expected arguments
        mock_html_of_table.assert_called_with(
            table=mock_sqlalchemy_table,
            template=mock_jinja_template,
            include_table_name=True,
            component_id=TestTool.COMPONENT_ID,
            table_transient_id=TestTool.TABLE_TRANSIENT_ID
        )
        # Check that the response has the expected body and content type
        mock_Response.assert_called_with(body=mock_template, content_type=consts.AIOHTTP_HTML)
        assert response == mock_response_instance

    def test_get_table_missing_table_name_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected requested table name to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_context_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected context to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_component_id_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected component id to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_table_transient_id_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected table transient id to be in request query"):
            asyncio.run(tool.get_table(request))

    @patch('coolNewLanguage.src.tool.web')
    def test_get_table_table_not_found(self, mock_web: Mock, tool: Tool, monkeypatch):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Monkey patch get_table_from_table_name
        monkeypatch.setattr('coolNewLanguage.src.tool.Tool.get_table_from_table_name', Mock(return_value=None))
        # Mock web.Response
        mock_response_instance = Mock()
        mock_Response = Mock(return_value=mock_response_instance)
        mock_web.Response = mock_Response

        # Do
        response = asyncio.run(tool.get_table(request))

        # Check
        mock_Response.assert_called_with(body="Table not found", status=404)
        assert response == mock_response_instance

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_table_select_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool, monkeypatch):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': consts.GET_TABLE_TABLE_SELECT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Monkey patch get_table_from_table_name
        monkeypatch.setattr('coolNewLanguage.src.tool.Tool.get_table_from_table_name', Mock())
        # Mock get_template behavior
        mock_get_template = Mock()
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Mock web.Response
        mock_web.Response = Mock()

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': Mock()}):
            asyncio.run(tool.get_table(request))

        # Check
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.TABLE_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME)

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_column_select_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool, monkeypatch):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': consts.GET_TABLE_COLUMN_SELECT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Monkey patch get_table_from_table_name
        monkeypatch.setattr('coolNewLanguage.src.tool.Tool.get_table_from_table_name', Mock())
        # Mock get_template behavior
        mock_get_template = Mock()
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Mock web.Response
        mock_web.Response = Mock()

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': Mock()}):
            asyncio.run(tool.get_table(request))

        # Check
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.COLUMN_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME)

    TABLE_NAME = 'cool_new_table'
    GET_TABLE_CONTEXT = 'get_table_context'
    COMPONENT_ID = 'component_id'
    TABLE_TRANSIENT_ID = 'table_transient_id'

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Prepare to patch db_utils.get_table_from_table_name
        mock_sqlalchemy_table = Mock()
        mock_get_table_from_table_name = Mock(return_value=mock_sqlalchemy_table)
        mock_db_utils = Mock(get_table_from_table_name=mock_get_table_from_table_name)
        mock_utils = Mock(db_utils=mock_db_utils)
        # Mock get_template behavior
        mock_jinja_template = Mock()
        mock_get_template = Mock(return_value=mock_jinja_template)
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Prepare to patch html_utils.html_of_table
        mock_template = Mock()
        mock_html_of_table = Mock(return_value=mock_template)
        mock_html_utils = Mock(html_of_table=mock_html_of_table)
        mock_utils.html_utils = mock_html_utils
        # Mock web.Response
        mock_response_instance = Mock()
        mock_Response = Mock(return_value=mock_response_instance)
        mock_web.Response = mock_Response

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': mock_utils}):
            response = asyncio.run(tool.get_table(request))

        # Check
        # Check that get_table_from_table_name was called with the expected arguments
        mock_get_table_from_table_name.assert_called_with(tool=tool, table_name=TestTool.TABLE_NAME)
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.TABLE_RESULT_TEMPLATE_FILENAME)
        # Check that html_of_table was called with the expected arguments
        mock_html_of_table.assert_called_with(
            table=mock_sqlalchemy_table,
            template=mock_jinja_template,
            include_table_name=True,
            component_id=TestTool.COMPONENT_ID,
            table_transient_id=TestTool.TABLE_TRANSIENT_ID
        )
        # Check that the response has the expected body and content type
        mock_Response.assert_called_with(body=mock_template, content_type=consts.AIOHTTP_HTML)
        assert response == mock_response_instance

    def test_get_table_non_web_request_request(self, tool: Tool):
        # Do, Check
        with pytest.raises(TypeError, match="Expected request to be an aiohttp web Request"):
            asyncio.run(tool.get_table(Mock()))

    def test_get_table_missing_table_name_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected requested table name to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_context_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected context to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_component_id_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected component id to be in request query"):
            asyncio.run(tool.get_table(request))

    def test_get_table_missing_table_transient_id_query_param(self, tool: Tool):
        # Setup
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID
        }

        # Do, Check
        with pytest.raises(ValueError, match="Expected table transient id to be in request query"):
            asyncio.run(tool.get_table(request))

    @patch('coolNewLanguage.src.tool.web')
    def test_get_table_table_not_found(self, mock_web: Mock, tool: Tool):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': TestTool.GET_TABLE_CONTEXT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Prepare to patch db_utils.get_table_from_table_name
        mock_get_table_from_table_name = Mock(return_value=None)
        mock_db_utils = Mock(get_table_from_table_name=mock_get_table_from_table_name)
        mock_utils = Mock(db_utils=mock_db_utils)
        # Mock web.Response
        mock_response_instance = Mock()
        mock_Response = Mock(return_value=mock_response_instance)
        mock_web.Response = mock_Response

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': mock_utils}):
            response = asyncio.run(tool.get_table(request))

        # Check
        mock_Response.assert_called_with(body="Table not found", status=404)
        assert response == mock_response_instance

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_table_select_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': consts.GET_TABLE_TABLE_SELECT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Mock get_template behavior
        mock_get_template = Mock()
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Mock web.Response
        mock_web.Response = Mock()

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': Mock()}):
            asyncio.run(tool.get_table(request))

        # Check
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.TABLE_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME)

    @patch('coolNewLanguage.src.tool.web')
    @patch('coolNewLanguage.src.tool.process')
    def test_get_table_column_select_happy_path(self, mock_process: Mock, mock_web: Mock, tool: Tool):
        # Setup
        # Mock web.Request so that the type check doesn't error
        mock_web.Request = web.Request
        # Construct the request
        request = Mock(spec=web.Request)
        request.query = {
            'table': TestTool.TABLE_NAME,
            'context': consts.GET_TABLE_COLUMN_SELECT,
            'component_id': TestTool.COMPONENT_ID,
            'table_transient_id': TestTool.TABLE_TRANSIENT_ID
        }
        # Mock get_template behavior
        mock_get_template = Mock()
        mock_jinja_environment = Mock(get_template=mock_get_template)
        mock_running_tool = Mock(jinja_environment=mock_jinja_environment)
        mock_process.running_tool = mock_running_tool
        # Mock web.Response
        mock_web.Response = Mock()

        # Do
        with patch.dict('sys.modules', {'coolNewLanguage.src.util': Mock()}):
            asyncio.run(tool.get_table(request))

        # Check
        # Check that the correct template was fetched
        mock_get_template.assert_called_with(name=consts.COLUMN_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME)

    @patch('coolNewLanguage.src.tool.process')
    def test_user_input_received(self, mock_process: Mock, tool: Tool):
        # Setup
        mock_handling_post = Mock()
        mock_process.handling_post = mock_handling_post

        # Do
        user_input_received = tool.user_input_received()

        # Check
        assert user_input_received == mock_handling_post