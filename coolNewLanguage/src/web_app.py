from aiohttp import web


class WebApp:
    def __init__(self):
        self.app = web.Application()

    def add_static_file_handler(self, route:str, fs_path:str):
        self.app.add_routes([web.static(route, fs_path)])