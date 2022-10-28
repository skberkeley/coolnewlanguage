from aiohttp import web


class WebApp:
    def __init__(self):
        self.app = web.Application()
