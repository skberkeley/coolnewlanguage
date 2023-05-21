from typing import Callable, List

import aiohttp_jinja2
import jinja2
import sqlalchemy
from aiohttp import web

from coolNewLanguage.src.consts import DATA_DIR, STATIC_ROUTE, STATIC_FILE_DIR, TEMPLATES_DIR, \
    LANDING_PAGE_TEMPLATE_FILENAME, LANDING_PAGE_STAGES
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.util.str_utils import check_has_only_alphanumerics_or_underscores
from coolNewLanguage.src.web_app import WebApp
from typing import List, Type, Any, Union

class Field:
    __slots__ = [
        "type", "optional"
    ]
    def __init__(self, type:type, optional:bool = False) -> None:
        self.type = type
        self.optional = optional

class CNLType:
    # __slots__ = [
    #     "__hls_backing_row",
    #     "__hls_typing"
    # ]
    def __init__(self, backing_row=None) -> None:
        self.__hls_backing_row = backing_row

    def fields(self):
        raise ValueError("Fields must be overridden")

    # def field_to_nested(self, __name:str):
    #     fields = Tool.__type_to_fields(self.__class__)
    #     if __name  fields:
    #     fields = Tool.__type_to_field_flattening(self.__class__)
    #     fields = 
    
    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return self.__hls_backing_row[__name]

    def _hls_type_to_fields(type:Type["CNLType"]):
        if not isinstance(type(), CNLType):
            raise TypeError("Expected a CNLType")
        instance = type()
        instance_fields_t0 = instance.__dict__.copy()
        instance.fields()
        instance_fields_t1 = instance.__dict__.copy()
        instance_fields = {
            k : v for k, v in instance_fields_t1.items()
            if k not in instance_fields_t0.keys()
        }

        return instance_fields
    
    def _hls_flatten_field(f:Field, hiearchical_name:str) -> dict:
        if isinstance(f.type(), CNLType):
            return CNLType._hls_type_to_field_flattening(f.type, hiearchical_name)
        else:
            return {hiearchical_name : f}
        
    def _hls_type_to_field_flattening(type:Type["CNLType"], hiearchical_name:str = None) -> dict:
        if not isinstance(type(), CNLType):
            raise TypeError("Expected a CNLType")
        
        instance_fields = CNLType._hls_type_to_fields(type)
        result = {}
        for (name, field) in instance_fields.items():
            h_name = f"{hiearchical_name}.{name}" if hiearchical_name else name
            result.update(CNLType._hls_flatten_field(field, h_name))
        return result
    
    def link(self, to:Any, on:"Link"):
        from coolNewLanguage.src.row import Row
        from coolNewLanguage.src.util.db_utils import link_create
        from coolNewLanguage.src.stage import process

        link_field = on._hls_internal_field
        link_id = on._hls_internal_link_id

        src_row_id:int = self.__hls_backing_row.row_id
        # src_table:int = self.__hls_backing_row.table.name
        dst_row_id:int
        dst_table:str
        if (isinstance(to, Row)):
            to:Row
            dst_row_id = to.row_id
            dst_table = to.table.name
        elif (isinstance(to, CNLType)):
            to:CNLType
            dst_row_id = to.__hls_backing_row.row_id
            dst_table = to.__hls_backing_row.table.name
        else:
            raise TypeError("Unexpected link target type")

        link = link_create(process.running_tool, link_id, src_row_id, dst_table, dst_row_id)
        print("Created link", link)


class Link:
    __slots__ = [
        "_hls_internal_field",
        "_hls_internal_link_id"
    ]
    
    def synthesize(field:str, link_id:int):
        l = Link()
        l._hls_internal_field = field
        l._hls_internal_link_id = link_id


class Tool:
    """
    A data processing tool

    Attributes:
    tool_name : str
    stages : list[Stage]
    url : str
    web_app : WebApp
    """
    def __init__(self, tool_name: str, url: str = ''):
        """
        Initialize this tool
        Starts the web_app which forms the back end of this tool
        Configures the Jinja environment used to render certain templates
        :param tool_name: The name of this tool, can only contain alphanumeric characters or underscores
        :param url: The url path for this tool, to be used in the future for situations with multiple tools
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


        self.tool_name = tool_name

        self.stages: List[Stage] = []

        if url == '':
            self.url = tool_name
        else:
            self.url = url

        self.web_app = WebApp()
        # add a handler for the web app's static files (like javascript stuff)
        self.web_app.add_static_file_handler(STATIC_ROUTE, str(STATIC_FILE_DIR))

        loader = jinja2.FileSystemLoader(TEMPLATES_DIR)
        # jinja environment used to render templates
        self.jinja_environment = jinja2.Environment(loader=loader)
        aiohttp_jinja2.setup(self.web_app.app, loader=loader)

        db_path = DATA_DIR.joinpath(f'{self.url}.db')
        # create an engine with a sqlite database
        self.db_engine = sqlalchemy.create_engine(f'sqlite:///{str(db_path)}', echo=True)
        # Connect to the engine, so that the sqlite db file is created if it doesn't exist already
        self.db_engine.connect()
        self.db_metadata_obj = sqlalchemy.MetaData()

        from coolNewLanguage.src.util.db_utils import db_awaken
        db_awaken(self)

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
        routes = [web.get('/', self.landing_page)]

        for stage in self.stages:
            routes.append(
                web.get(f'/{stage.url}', stage.handle)
            )
            routes.append(
                web.post(f'/{stage.url}/post', stage.post_handler)
            )

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

    def create_table(self, name:str, type:Type[CNLType]):
        from coolNewLanguage.src.util.db_utils import create_table_if_not_exists, link_register
        flatten_fields = CNLType._hls_type_to_field_flattening(type)

        columns = [n for (n, _) in flatten_fields.items()]
        print(f"new fields {columns}")

        # links = {}
        instance_fields = {}
        for (k, v) in flatten_fields.items():
            v:Field
            if (isinstance(v.type(), Link)):
                link_id = link_register(self, name, k)
                print("Registering link:", )
                link = Link()
                link._hls_internal_field = k
                link._hls_internal_link_id = link_id
                setattr(type, k, link)
            else:
                instance_fields[k] = v
        create_table_if_not_exists(self, name, instance_fields)

    def create_global_link(self, name:str) -> "Link":
        from coolNewLanguage.src.util.db_utils import link_register
        link_id = link_register(self, "__hls_global", name)

        return Link.synthesize(name, link_id)

