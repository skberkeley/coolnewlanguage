import urllib.parse
from typing import Callable

import aiohttp_jinja2
import jinja2
import sqlalchemy
from aiohttp import web

from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.component.submit_component import SubmitComponent
from coolNewLanguage.src.consts import DATA_DIR
from coolNewLanguage.src.stage.config import Config
from coolNewLanguage.src.stage.process import Process
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.web_app import WebApp


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
        :param tool_name: The name of this tool
        :param url: The url for this tool, to be used in the future for situations with multiple tools
        """
        if not isinstance(tool_name, str):
            raise TypeError("Expected a string for Tool name")
        self.tool_name = tool_name

        self.stages = []

        if not isinstance(url, str):
            raise TypeError("Expected a string for tool url")
        if url == '':
            self.url = tool_name
        else:
            self.url = url

        self.web_app = WebApp()
        self.web_app.add_static_file_handler('/static', 'coolNewLanguage/web/static')
        loader = jinja2.FileSystemLoader('coolNewLanguage/web/templates')
        self.jinja_environment = jinja2.Environment(loader=loader)
        aiohttp_jinja2.setup(self.web_app.app, loader=loader)

        db_path = DATA_DIR.joinpath(f'{self.url}.db')
        self.db_engine = sqlalchemy.create_engine(f'sqlite:///{str(db_path)}', echo=True)
        self.db_metadata_obj = sqlalchemy.MetaData()

    def add_stage(self, stage_name: str, stage_func: Callable):
        """
        Add a stage to this tool
        Pre-render the stage's Config by running stage_func, and having each Component paint itself and append to
        a template list
        :param stage_name: The name of this stage
        :param stage_func: The function used to define this stage
        :return:
        """
        stage_url = urllib.parse.quote(stage_name)
        form_action = f'/{stage_url}/post'
        form_method = "post"

        Config.template_list = [
            '<html>',
            '<head>',
            '<script src="/static/support.js">',
            '</script>',
            '<title>',
            stage_name,
            '</title>',
            '</head>',
            '<body>',
            f'<form action="{form_action}" method="{form_method}" enctype="multipart/form-data">'
        ]
        stack = ['</html>', '</body>', '</form>']
        Config.submit_component_added = False
        Config.building_template = True
        Config.tool_under_construction = self
        # num_components is used for id's in the HTML template
        Component.num_components = 0

        # call the stage_func, so that each component adds to Config.template_list
        stage_func()

        if not Config.submit_component_added:
            SubmitComponent("Submit")

        while stack:
            Config.template_list.append(stack.pop())

        Config.tool_under_construction = None
        Config.building_template = False

        template = ''.join(Config.template_list)

        new_stage = Stage(stage_name, template, stage_func)
        self.stages.append(new_stage)

        # reset num_components
        Component.num_components = 0

    def run(self):
        """
        Run this tool using aiohttp
        Add a landing page route, and the requisite stages for each stage
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

        Process.running_tool = self

        web.run_app(self.web_app.app, port=8000)

    async def landing_page(self, request: web.Request) -> web.Response:
        """
        The landing page handler for this tool
        Returns a template with links to each stage
        :param request:
        :return:
        """
        return aiohttp_jinja2.render_template(
            template_name='list_stages_landing_page.html',
            request=request,
            context={
                'stages': self.stages
            }
        )
