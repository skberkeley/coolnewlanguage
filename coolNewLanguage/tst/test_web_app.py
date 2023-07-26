from unittest.mock import Mock

import aiohttp.web
import pytest

from coolNewLanguage.src.web_app import WebApp

class TestWebApp:
    ROUTE = "route"
    FS_HANDLER = "fs_handler"

    @pytest.fixture
    def web_app(self) -> WebApp:
        return WebApp()

    def test_web_app_happy_path(self):
        # Do
        web_app = WebApp()

        # Check
        assert isinstance(web_app.app, aiohttp.web.Application)

    def test_add_static_file_handler_happy_path(self, web_app: WebApp):
        # Setup
        web_app.app.add_routes = Mock()

        # Do
        web_app.add_static_file_handler(TestWebApp.ROUTE, TestWebApp.FS_HANDLER)

        # Check
        web_app.app.add_routes.assert_called()

    def test_add_static_file_handler_non_string_route(self, web_app: WebApp):
        # Do, Check
        with pytest.raises(TypeError):
            web_app.add_static_file_handler(Mock(), TestWebApp.FS_HANDLER)

    def test_add_static_file_handler_non_string_fs_path(self, web_app: WebApp):
        # Do, Check
        with pytest.raises(TypeError):
            web_app.add_static_file_handler(TestWebApp.ROUTE, Mock())
