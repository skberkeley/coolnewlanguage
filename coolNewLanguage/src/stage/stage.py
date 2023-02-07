import urllib
from typing import Callable

from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.component import Component


class Stage:
    """
    A stage of a data processing tool
    Provides two endpoints for the associated Tool's webapp
    handle provides the initial endpoint when the stage is first
    viewed, and returns the stage's Config, which was pre-rendered
    post_handler provides the endpoint when the input from Config is submitted
    and handles processing data correctly and displaying the results

    Attributes:
        handling_post:
            Whether a post request is currently being handled
            Used by other classes to determine current execution mode
        post_body:
            The body of the post request being handled
            Used by InputComponents to bind the results of input frm users
        results_template:
            The rendered Jinja template containing any relevant results
            Set here by show_results() so that we have access
            to it outside the scope of the stage_func call
    """
    handling_post = False
    post_body = None
    results_template = None

    def __init__(self, name: str, template: str, stage_func: Callable):
        """
        Initialize this stage. The stage url is generated from the passed name
        :param name: This stage's name
        :param template: The pre-rendered template for this stage's Config
        :param stage_func: The function used to define this stage
        """
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
        """
        Handles initial get request for this stage by returning the pre-rendered Config template
        :param request:
        :return:
        """
        jinja_template = consts.JINJA_ENV.from_string(self.template)
        rendered_template = jinja_template.render()
        return web.Response(body=rendered_template, content_type=consts.AIOHTTP_HTML)

    async def post_handler(self, request: web.Request) -> web.Response:
        """
        Handles post request with user input
        First gets post body to make it available for InputComponents to bind their values
        Then, re-runs stage_func with handling_post flag set to True
        This causes Processors to run, and for Components to try to get their values from the post body
        It also causes show_result to run, and to try to render the results template so that it can be returned in the
        response
        If results is not set, we just redirect back to the tool landing page
        :param request:
        :return:
        """
        Stage.post_body = await request.post()
        Stage.handling_post = True
        Component.num_components = 0

        self.stage_func()

        Stage.post_body = None
        Stage.handling_post = False
        Component.num_components = 0

        if Stage.results_template is not None:
            template = Stage.results_template
            Stage.results_template = None

            return web.Response(body=template, content_type=consts.AIOHTTP_HTML)
        else:
            raise web.HTTPFound('/')
