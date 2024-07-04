import pathlib
from typing import Callable, Optional

import aiohttp_jinja2
import jinja2
import pandas as pd
import sqlalchemy
from aiohttp import web

import coolNewLanguage.src.tables as tables
import coolNewLanguage.src.util.sql_alch_csv_utils as sql_alch_csv_utils

from coolNewLanguage.src import consts
from coolNewLanguage.src.consts import DATA_DIR, STATIC_ROUTE, STATIC_FILE_DIR, TEMPLATES_DIR, \
    LANDING_PAGE_TEMPLATE_FILENAME, LANDING_PAGE_STAGES, STYLES_ROUTE, STYLES_DIR
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.util.str_utils import check_has_only_alphanumerics_or_underscores
from coolNewLanguage.src.web_app import WebApp
from typing import List


class Tool:
    """
    A data processing tool

    Attributes:
    tool_name : str
    stages : list[Stage]
    url : str
    web_app : WebApp
    file_dir : Pathlib.Path - A path to the directory in which to store files uploaded to this Tool
    state : dict - A dictionary programmers can use to share state between Stages
    """
    def __init__(self, tool_name: str, url: str = '', file_dir_path: str = ''):
        """
        Initialize this tool
        Initializes the web_app which forms the back end of this tool
        Configures the Jinja environment used to render certain templates
        :param tool_name: The name of this tool, can only contain alphanumeric characters or underscores
        :param url: The url path for this tool, to be used in the future for situations with multiple tools
        :param file_dir_path: A path to the directory in which to store files uploaded to this Tool
        """
        if not isinstance(tool_name, str):
            raise TypeError("Expected a string for Tool name")
        # This restriction on tool names allows them to be used as the URL paths
        if not check_has_only_alphanumerics_or_underscores(tool_name):
            raise ValueError("Tool name can only contain alphanumeric characters and underscores")
        if not isinstance(url, str):
            raise TypeError("Expected a string for Tool url")
        if len(url) > 0 and not check_has_only_alphanumerics_or_underscores(url):
            raise ValueError("Tool url can only contain alphanumeric characters and underscores")
        if not isinstance(file_dir_path, str):
            raise TypeError("Expected file_dir_path to be a string")


        self.tool_name = tool_name

        self.stages: List[Stage] = []

        if url == '':
            self.url = tool_name
        else:
            self.url = url

        self.web_app = WebApp()
        # add a handler for the web app's static files (like javascript stuff)
        self.web_app.add_static_file_handler(STATIC_ROUTE, str(STATIC_FILE_DIR))
        self.web_app.add_static_file_handler(STYLES_ROUTE, str(STYLES_DIR))

        loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
        # jinja environment used to render templates
        self.jinja_environment = jinja2.Environment(loader=loader)
        aiohttp_jinja2.setup(self.web_app.app, loader=loader)

        # create the data directory if it doesn't exist
        DATA_DIR.mkdir(exist_ok=True)

        db_path = DATA_DIR.joinpath(f'{self.url}.db')
        # create an engine with a sqlite database
        self.db_engine: sqlalchemy.Engine = sqlalchemy.create_engine(f'sqlite:///{str(db_path)}', echo=True)
        # Connect to the engine, so that the sqlite db file is created if it doesn't exist already
        self.db_engine.connect()
        self.db_metadata_obj: sqlalchemy.MetaData = sqlalchemy.MetaData()

        # Awakening the db creates the necessary tables required to run the tool
        self.db_awaken()

        # Create a directory to store uploaded files
        if file_dir_path == '':
            self.file_dir = consts.FILES_DIR.joinpath(tool_name)
        else:
            self.file_dir = pathlib.Path(file_dir_path)
        self.file_dir.mkdir(parents=True, exist_ok=True)

        self.state = {}

        self.tables = tables.Tables(self)

    def add_stage(self, stage_name: str, stage_func: Callable):
        """
        Add a stage to this tool
        Pre-render the stage's Config by running stage_func, and having each Component paint itself and append to
        a template list
        :param stage_name: The name of this stage
        :param stage_func: The function used to define this stage
        :return:
        """
        if not isinstance(stage_name, str):
            raise TypeError("Expected stage_name to be a string")
        if not callable(stage_func):
            raise TypeError("Expected stage_func to be callable")
        new_stage = Stage(stage_name, stage_func)
        self.stages.append(new_stage)

    def run(self):
        """
        Run this tool using aiohttp
        Add a landing page route, and the requisite routes for each stage
        :return:
        """
        from coolNewLanguage.src.approvals import approvals

        routes = [
            web.get('/', self.landing_page),
            web.get(consts.GET_TABLE_ROUTE, self.get_table)
        ]

        for stage in self.stages:
            routes.append(web.get(f'/{stage.url}', stage.handle))
            routes.append(web.post(f'/{stage.url}/post', stage.post_handler))
            routes.append(web.post(f'/{stage.url}/approve', approvals.approval_handler))

        self.web_app.app.add_routes(routes)

        process.running_tool = self

        web.run_app(self.web_app.app, port=8000)

    async def landing_page(self, request: web.Request) -> web.Response:
        """
        The landing page handler for this tool
        Returns a template with links to each stage
        :param request:
        :return:
        """
        if not isinstance(request, web.Request):
            raise TypeError("Expected request to be an aiohttp web Request")

        return aiohttp_jinja2.render_template(
            template_name=LANDING_PAGE_TEMPLATE_FILENAME,
            request=request,
            context={
                LANDING_PAGE_STAGES: self.stages
            }
        )

    def create_table(self, name: str, cnl_type: type['CNLType']):
        """
        Creates a new Table in this Tool's backend, with the given name and columns matching the fields of the passed
        CNLType subclass. Doesn't create columns for Fields of type Link; instead, registers the Link metatype for each
        one.
        :param name: The name to give the created table
        :param cnl_type: The CNLType subclass from which to infer the columns to be created
        :return:
        """
        from coolNewLanguage.src.util import db_utils, link_utils
        from coolNewLanguage.src.cnl_type.cnl_type import CNLType
        from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype

        table_fields = {}
        cnl_type_fields = CNLType.CNL_type_to_fields(cnl_type)

        for field_name, field_instance in cnl_type_fields.items():
            if isinstance(field_instance.data_type, LinkMetatype):
                link_utils.register_link_metatype_on_tool(tool=self, link_meta_name=field_instance.data_type.meta_name)
            else:
                table_fields[field_name] = field_instance

        db_utils.create_table_if_not_exists(tool=self, table_name=name, fields=table_fields)

    def register_link_metatype(self, link_meta_name: str) -> "Link":
        """
        Registers a new link metatype. Provides an API for registering a new link metatype separate from adding a Field
        of type Link to a CNLType subclass.
        :param link_meta_name:
        :return:
        """
        from coolNewLanguage.src.cnl_type.link_metatype import LinkMetatype
        from coolNewLanguage.src.util.link_utils import register_link_metatype_on_tool

        if not isinstance(link_meta_name, str):
            raise TypeError("Expected link_meta_name to be a string")

        register_link_metatype_on_tool(tool=self, link_meta_name=link_meta_name)

        return LinkMetatype(name=link_meta_name)

    async def get_table(self, request: web.Request) -> web.Response:
        from coolNewLanguage.src.util import html_utils
        if "table" not in request.query:
            raise ValueError("Expected requested table name to be in request query")
        table_name = request.query["table"]
        if "context" not in request.query:
            raise ValueError("Expected context to be in request query")
        context = request.query["context"]
        if "component_id" not in request.query:
            raise ValueError("Expected component id to be in request query")
        component_id = request.query["component_id"]
        if "table_transient_id" not in request.query:
            raise ValueError("Expected table transient id to be in request query")
        table_transient_id = request.query["table_transient_id"]

        sqlalchemy_table = self.get_table_from_table_name(table_name)
        if sqlalchemy_table is None:
            return web.Response(body="Table not found", status=404)

        # select correct jinja template
        if context == consts.GET_TABLE_TABLE_SELECT:
            template: jinja2.Template = process.running_tool.jinja_environment.get_template(
                name=consts.TABLE_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME
            )
        elif context == consts.GET_TABLE_COLUMN_SELECT:
            template: jinja2.Template = process.running_tool.jinja_environment.get_template(
                name=consts.COLUMN_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME
            )
        else:
            template: jinja2.Template = process.running_tool.jinja_environment.get_template(
                name=consts.TABLE_RESULT_TEMPLATE_FILENAME
            )

        template: str = html_utils.html_of_table(
            table=sqlalchemy_table,
            template=template,
            include_table_name=True,
            component_id=component_id,
            table_transient_id=table_transient_id
        )

        return web.Response(body=template, content_type=consts.AIOHTTP_HTML)

    def get_table_from_table_name(self, table_name: str) -> Optional[sqlalchemy.Table]:
        """
        Get the sqlalchemy Table which has the given name
        :param table_name: The name of the table which we try to get
        :return: The Table with matching name
        """
        insp: sqlalchemy.Inspector = sqlalchemy.inspect(self.db_engine)

        if not insp.has_table(table_name):
            return None
        table = sqlalchemy.Table(table_name, self.db_metadata_obj)
        insp.reflect_table(table, None)

        return table

    def db_awaken(self):
        """
        Creates/gets necessary tables in backend, and is called when the tool is instantiated
        Creates the LINKS_META table, which encodes the existing Link metatypes, and the LINKS table, which acts as a
        registry of the individual links themselves.
        :return:
        """
        if self.get_table_from_table_name(consts.LINKS_METATYPES_TABLE_NAME) is None:
            cols = [
                sqlalchemy.Column(
                    consts.LINKS_METATYPES_LINK_META_ID,
                    sqlalchemy.Integer,
                    sqlalchemy.Identity(),
                    primary_key=True),
                sqlalchemy.Column(consts.LINKS_METATYPES_LINK_META_NAME, sqlalchemy.String, nullable=False, unique=True)
            ]
            links_metatypes_table = sqlalchemy.Table(consts.LINKS_METATYPES_TABLE_NAME, self.db_metadata_obj, *cols)
            links_metatypes_table.create(self.db_engine)

        if self.get_table_from_table_name(consts.LINKS_REGISTRY_TABLE_NAME) is None:
            cols = [
                sqlalchemy.Column(
                    consts.LINKS_REGISTRY_LINK_ID,
                    sqlalchemy.Integer,
                    sqlalchemy.Identity(),
                    primary_key=True),
                sqlalchemy.Column(consts.LINKS_REGISTRY_LINK_META_ID, sqlalchemy.Integer, nullable=False),
                sqlalchemy.Column(consts.LINKS_REGISTRY_SRC_TABLE_NAME, sqlalchemy.String, nullable=False),
                sqlalchemy.Column(consts.LINKS_REGISTRY_SRC_ROW_ID, sqlalchemy.Integer, nullable=False),
                sqlalchemy.Column(consts.LINKS_REGISTRY_DST_TABLE_NAME, sqlalchemy.String, nullable=False),
                sqlalchemy.Column(consts.LINKS_REGISTRY_DST_ROW_ID, sqlalchemy.Integer, nullable=False)
            ]
            links_registry_table = sqlalchemy.Table(consts.LINKS_REGISTRY_TABLE_NAME, self.db_metadata_obj, *cols)
            links_registry_table.create(self.db_engine)

    def get_table_dataframe(self, table_name: str) -> Optional[pd.DataFrame]:
        if not isinstance(table_name, str):
            raise TypeError("Expected table_name to be a string")

        table = self.get_table_from_table_name(table_name)

        if table is None:
            return None

        with self.db_engine.connect() as conn:
            return pd.read_sql(sqlalchemy.select(table), conn)
