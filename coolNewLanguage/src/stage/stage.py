import urllib
from typing import Callable

from aiohttp import web

from coolNewLanguage.src import util
from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.processor.processor import Processor


class Stage:
    def __init__(self, name: str, template: str, stage_func: Callable):
        if not isinstance(name, str):
            raise TypeError("name of a stage should be a string")
        self.name = name

        if not isinstance(template, str):
            raise TypeError("template of a stage should be a string")
        self.template = template

        if not isinstance(stage_func, Callable):
            raise TypeError("stagefunc of a stage should be a function")
        self.stage_func = stage_func

        self.url = urllib.parse.quote(name)

    async def handle(self, request: web.Request) -> web.Response:
        jinja_template = util.JINJA_ENV.from_string(self.template)
        rendered_template = jinja_template.render()
        return web.Response(body=rendered_template, content_type=util.AIOHTTP_HTML)

    async def post_handler(self, request: web.Request) -> web.Response:
        Processor.post_body = await request.post()
        Processor.run_process = True
        Component.num_components = 0
        self.stage_func()
        Processor.post_body = None
        Processor.run_process = False
        raise web.HTTPFound('/')
