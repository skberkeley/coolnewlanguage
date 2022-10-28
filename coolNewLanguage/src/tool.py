from typing import List

import aiohttp_jinja2
import jinja2
from aiohttp import web

from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.web_app import WebApp


class Tool:
    def __init__(self, tool_name: str, stages: List[Stage], url: str = ''):
        if not isinstance(tool_name, str):
            raise TypeError("Expected a string for Tool name")
        self.tool_name = tool_name

        if not all([isinstance(s, Stage) for s in stages]):
            raise TypeError("Every passed stage should be a stage")
        if len(stages) != len(set([s.name for s in stages])):
            raise ValueError("Every stage should have a unique name")
        self.stages = stages

        if not isinstance(url, str):
            raise TypeError("Expected a string for tool url")
        if url == '':
            self.url = tool_name
        else:
            self.url = url

        self.web_app = WebApp()
        aiohttp_jinja2.setup(self.web_app.app, loader=jinja2.FileSystemLoader('coolNewLanguage/static/templates'))

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
