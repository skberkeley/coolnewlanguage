import asyncio
import os.path
import pathlib
from unittest.mock import patch, Mock, NonCallableMock

import pytest
import sqlalchemy
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype
from coolNewLanguage.src.consts import STATIC_ROUTE, STATIC_FILE_DIR, TEMPLATES_DIR, LANDING_PAGE_TEMPLATE_FILENAME,\
    LANDING_PAGE_STAGES
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.web_app import WebApp
from coolNewLanguage.tst.cnl_type.cnl_type_test_utils import MyFirstType


class TestTool:
    TOOL_NAME = "OSKI_TOOL"
    TOOL_URL = "OSKI"
    STAGE_NAME = "The Wizard of Woz"
    STAGE_FUNC = Mock()
    FILE_DIR_PATH = "a/real/path"

    @patch('aiohttp_jinja2.setup')
    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    @patch.object(WebApp, 'add_static_file_handler')
    def test_tool_happy_path(self,
                             mock_add_static_file_handler: Mock,
                             mock_FileSystemLoader: Mock,
                             mock_Environment: Mock,
                             mock_aiohttp_jinja2_setup: Mock,
                             tmp_path: pathlib.Path,
                             monkeypatch):
        # Setup
        mock_file_system_loader = mock_FileSystemLoader.return_value
        mock_environment = mock_Environment.return_value
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)

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
        mock_add_static_file_handler.assert_called_with(STATIC_ROUTE, str(STATIC_FILE_DIR))
        # loader was created with templates dir
        mock_FileSystemLoader.assert_called_with(TEMPLATES_DIR)
        # jinja environment was created with loader
        mock_Environment.assert_called_with(loader=mock_file_system_loader)
        assert tool.jinja_environment is mock_environment
        # aiohttp jinja setup was called appropriately
        mock_aiohttp_jinja2_setup.assert_called_with(tool.web_app.app, loader=mock_file_system_loader)
        # db engine was created
        assert isinstance(tool.db_engine, sqlalchemy.Engine)
        # sqlite file was created
        expected_db_path = tmp_path.joinpath(f'{TestTool.TOOL_URL}.db')
        assert os.path.exists(expected_db_path)
        # metadata obj was created
        assert isinstance(tool.db_metadata_obj, sqlalchemy.MetaData)
        # file_dir was set correctly
        expected_file_dir = consts.FILES_DIR.joinpath(TestTool.TOOL_NAME)
        assert tool.file_dir == expected_file_dir

    def test_tool_no_url_happy_path(self, tmp_path: pathlib.Path, monkeypatch):
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

    @patch('aiohttp_jinja2.setup')
    @patch('jinja2.Environment')
    @patch('jinja2.FileSystemLoader')
    def test_tool_custom_file_dir_path(
            self,
            mock_FileSystemLoader: Mock,
            mock_Environment: Mock,
            mock_aiohttp_jinja2_setup: Mock,
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


    @pytest.fixture
    def tool(self, tmp_path: pathlib.Path, monkeypatch) -> Tool:
        # Monkey patch DATA_DIR so that the database is created in tmp_path
        monkeypatch.setattr('coolNewLanguage.src.tool.DATA_DIR', tmp_path)
        monkeypatch.setattr('coolNewLanguage.src.tool.STATIC_FILE_DIR', tmp_path)

        return Tool(tool_name=TestTool.TOOL_NAME, url=TestTool.TOOL_URL)

    @patch('coolNewLanguage.src.tool.Stage')
    def test_add_stage_happy_path(self, mock_Stage: Mock, tool: Tool):
        # Setup
        mock_stage = mock_Stage.return_value

        # Do
        tool.add_stage(TestTool.STAGE_NAME, TestTool.STAGE_FUNC)

        # Check
        mock_Stage.assert_called_with(TestTool.STAGE_NAME, TestTool.STAGE_FUNC)
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
        # Add a stage to the tool
        tool.add_stage(TestTool.STAGE_NAME, TestTool.STAGE_FUNC)
        # Mock the Stage instantiation happening inside add_stage


        # Do
        tool.run()

        # Check
        # Construct the table of expected routes
        # Landing page route, GET and POST routes for stage that was added
        routes = [
            web.get('/', tool.landing_page),
            web.get(f'/{tool.stages[0].url}', tool.stages[0].handle),
            web.post(f'/{tool.stages[0].url}/post', tool.stages[0].post_handler)
        ]
        # Check that add_routes was called with the expected routes
        mock_add_routes.assert_called_with(routes)
        # Check that tool has been assigned to process.running_tool
        assert process.running_tool is tool
        # Check that web.run_app was called appropriately
        mock_run_app.assert_called_with(tool.web_app.app, port=8000)

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

    @patch('coolNewLanguage.src.util.link_utils.register_link_metatype_on_tool')
    @patch('coolNewLanguage.src.util.db_utils.create_table_if_not_exists')
    @patch.object(CNLType, 'CNL_type_to_fields')
    def test_create_table(
            self,
            mock_CNL_type_to_fields: Mock,
            mock_create_table_if_not_exists: Mock,
            mock_register_link_metatype: Mock,
            tool: Tool):
        # Setup
        field1, field2 = Mock(spec=Field), Mock(spec=Field)
        link_name = 'Zelda'
        link_field = Mock(spec=Field, data_type=Mock(spec=LinkMetatype, meta_name=link_name))
        table_name = 'cool_new_table'
        # Mock MyFirstType's CNL_type_to_fields
        mock_CNL_type_to_fields.return_value = {'field1': field1, 'field2': field2, 'link_field': link_field}

        # Do
        tool.create_table(table_name, MyFirstType)

        # Check
        # Check that create table was called
        mock_create_table_if_not_exists.assert_called_with(
            tool=tool,
            table_name=table_name,
            fields={'field1': field1, 'field2': field2}
        )
        # Check that register_link_metatype was called
        mock_register_link_metatype.assert_called_with(tool=tool, link_meta_name=link_name)
