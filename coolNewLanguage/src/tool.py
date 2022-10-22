from aiohttp import web

from coolNewLanguage.src import cool_new_webapp
from coolNewLanguage.src.page.page import Page


class Tool:
    def __init__(self, tool_name: str, home_page: Page, *pages: Page, url: str = ''):
        if not isinstance(tool_name, str):
            raise TypeError("Expected a string for Tool name")
        self.tool_name = tool_name

        if not isinstance(home_page, Page):
            raise TypeError("Expected a Page for Tool home page")
        self.home_page = home_page

        if not all([isinstance(p, Page) for p in pages]):
            raise TypeError("Something that wasn't a Page was passed to the Tool")
        self.pages = pages

        if not isinstance(url, str):
            raise TypeError("Expected a string for tool url")
        if url == '':
            self.url = tool_name
        else:
            self.url = url

        self.templates = {}

        cool_new_webapp.tools.append(self)

    def run(self):
        cool_new_webapp.app.add_routes(
            [
                web.get(f'/{self.tool_name}', self.home_page.handle)
            ]
        )
        web.run_app(cool_new_webapp.app, port=8000)
