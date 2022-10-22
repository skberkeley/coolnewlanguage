import aiohttp_jinja2
import jinja2
from aiohttp import web


class WebApp:
    def __init__(self):
        self.app = web.Application()

        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader('coolNewLanguage/static/templates'))

        self.app.add_routes(
            [
                web.get('/', self.list_tools)
            ]
        )

        self.tools = []

    async def list_tools(self, request):
        return aiohttp_jinja2.render_template(
            template_name='list_tools.html',
            request=request,
            context={
                'tool_list': self.tools
            }
        )
