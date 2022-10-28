import urllib.parse
from typing import List

from aiohttp import web

from coolNewLanguage.src import util
from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage.process import Process
from coolNewLanguage.src.stage.results import Results


class Stage:
    def __init__(self, name: str, config: List[Component], process: Process | None, results: Results | None):
        if not isinstance(name, str):
            raise TypeError("name of a stage should be a string")
        self.name = name

        if not all([isinstance(c, Component) for c in config]):
            raise TypeError("config of a stage should be a list of Components")
        self.config = config

        if not isinstance(process, Process) and process is not None:
            raise TypeError("process of a stage should be of type Process or None")
        self.process = process

        if not isinstance(results, Results) and results is not None:
            raise TypeError("results of a stage should be of type Results or None")
        self.results = results

        self.url = urllib.parse.quote(name)

    def paint_config(self) -> str:
        """
        Paint the html template for the config of this stage
        :return: A string containing the jinja2 template for the config
        """
        template_list = ['<html>', '<head>', '<title>', self.name, '</title>', '</head>', '<body>']
        stack = ['</html>', '</body>']

        for component in self.config:
            template_list.append(component.paint())

        while stack:
            template_list.append(stack.pop())

        return ''.join(template_list)

    async def handle(self, request: web.Request) -> web.Response:
        template_string = self.paint_config()
        jinja_template = util.JINJA_ENV.from_string(template_string)
        rendered_template = jinja_template.render()
        return web.Response(body=rendered_template, content_type=util.AIOHTTP_HTML)
