import urllib.parse
from typing import Callable

import aiohttp_jinja2
import jinja2
from aiohttp import web

from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.component.submit_component import SubmitComponent
from coolNewLanguage.src.stage.config import Config
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.web_app import WebApp


class Tool:
    def __init__(self, tool_name: str, url: str = ''):
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
        aiohttp_jinja2.setup(self.web_app.app, loader=jinja2.FileSystemLoader('coolNewLanguage/static/templates'))

    def add_stage(self, stage_name: str, stage_func: Callable):
        stage_url = urllib.parse.quote(stage_name)
        form_action = f'/{stage_url}/post'
        form_method = "post"

        Config.template_list = [
            '<html>',
            '<head>',
            '<title>',
            stage_name,
            '</title>',
            '</head>',
            '<body>',
            f'<form action="{form_action}" method="{form_method}">'
        ]
        stack = ['</html>', '</body>', '</form>']
        Config.submit_component_added = False
        Config.building_template = True
        Component.num_components = 0

        stage_func()

        if not Config.submit_component_added:
            SubmitComponent("Go back")

        while stack:
            Config.template_list.append(stack.pop())

        Config.building_template = False

        template = ''.join(Config.template_list)

        new_stage = Stage(stage_name, template, stage_func)
        self.stages.append(new_stage)

    def run(self):
        """
        Run this tool using aiohttp
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

        web.run_app(self.web_app.app, port=8000)

    async def landing_page(self, request: web.Request) -> web.Response:
        return aiohttp_jinja2.render_template(
            template_name='list_stages_landing_page.html',
            request=request,
            context={
                'stages': self.stages
            }
        )
