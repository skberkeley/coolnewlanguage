import jinja2
from aiohttp import web

from coolNewLanguage.src.component.component import Component


class Page:
    def __init__(self, title: str, *components: Component):
        if not isinstance(title, str):
            raise TypeError("Expected a string for Page title")
        self.title = title

        if not all([isinstance(c, Component) for c in components]):
            raise TypeError("Got something that wasn't a Component for this Page")
        self.components = components

        self.jinja_env = jinja2.Environment(loader=jinja2.BaseLoader())

    def paint(self) -> str:
        """
        Paint this page as a Jinja template
        If this page can be painted statically,
        return a regular HTML doc
        :return:
        """
        template = f'<html><head><title>{self.title}</title></head><body>'
        stack = ['</html>', '</body>']

        for component in self.components:
            template += component.paint()

        while stack:
            template += stack.pop()

        return template

    async def handle(self, request: web.Request) -> web.StreamResponse:
        template_string = self.paint()
        jinja_template = self.jinja_env.from_string(template_string)
        rendered_template = jinja_template.render()
        return web.Response(body=rendered_template, content_type='text/html')
