from aiohttp import web


class WebApp:
    """
    A wrapper class around the aiohttp web App actually used to run a Tool.

    Attributes:
        app:
            The aiohttp web app instance being wrapped
    """

    def __init__(self) -> None:
        self.app = web.Application(client_max_size=1024**3)

    def add_static_file_handler(self, route: str, fs_path: str) -> None:
        """
        Adds a static file handler by accessing the underlying aiohttp web app
        :param route: The URL prefix representing the static route
        :param fs_path: The path to the static folder
        :return:
        """
        if not isinstance(route, str):
            raise TypeError("Expected route to be a string")
        if not isinstance(fs_path, str):
            raise TypeError("Expected fs_path to be a string")
        self.app.add_routes([web.static(route, fs_path)])
