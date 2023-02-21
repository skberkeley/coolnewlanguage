import urllib
from typing import Callable

from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.component.submit_component import SubmitComponent
from coolNewLanguage.src.stage import process, config, results


class Stage:
    """
    A stage of a data processing tool
    Provides two endpoints for the associated Tool's webapp
    handle provides the initial endpoint when the stage is first
    viewed, and returns the stage's Config, which it renders when the request is made
    post_handler provides the endpoint when the input from Config is submitted
    and handles processing data correctly and displaying the results

    Attributes:
        results_template:
            The rendered Jinja template containing any relevant results
            Set here by show_results() so that we have access
            to it outside the scope of the stage_func call
    """

    def __init__(self, name: str, stage_func: Callable):
        """
        Initialize this stage. The stage url is generated from the passed name
        :param name: This stage's name
        :param template: The pre-rendered template for this stage's Config
        :param stage_func: The function used to define this stage
        """
        if not isinstance(name, str):
            raise TypeError("name of a stage should be a string")
        self.name = name

        if not isinstance(stage_func, Callable):
            raise TypeError("stagefunc of a stage should be a function")
        self.stage_func = stage_func

        self.url = urllib.parse.quote(name)

    async def handle(self, request: web.Request) -> web.Response:
        """
        Handles get request for this stage by painting this stage and returning the rendered template
        :param request:
        :return:
        """
        template = self.paint()
        jinja_template = consts.JINJA_ENV.from_string(template)
        rendered_template = jinja_template.render()
        return web.Response(body=rendered_template, content_type=consts.AIOHTTP_HTML)

    def paint(self) -> str:
        stage_url = urllib.parse.quote(self.name)
        form_action = f'/{stage_url}/post'
        form_method = "post"

        config.template_list = [
            '<html>',
            '<head>',
            '<script src="/static/support.js">',
            '</script>',
            '<title>',
            self.name,
            '</title>',
            '</head>',
            '<body>',
            f'<form action="{form_action}" method="{form_method}" enctype="multipart/form-data">'
        ]
        stack = ['</html>', '</body>', '</form>']
        config.submit_component_added = False
        config.building_template = True
        config.tool_under_construction = process.running_tool
        # num_components is used for id's in the HTML template
        Component.num_components = 0

        # call the stage_func, so that each component adds to config.template_list
        self.stage_func()

        if not config.submit_component_added:
            SubmitComponent("Submit")

        while stack:
            config.template_list.append(stack.pop())

        config.tool_under_construction = None
        config.building_template = False

        template = ''.join(config.template_list)

        # reset num_components
        Component.num_components = 0

        return template

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
        process.post_body = await request.post()
        process.handling_post = True
        Component.num_components = 0

        self.stage_func()

        process.post_body = None
        process.handling_post = False
        Component.num_components = 0

        if results.results_template is not None:
            template = results.results_template
            results.results_template = None

            return web.Response(body=template, content_type=consts.AIOHTTP_HTML)
        else:
            raise web.HTTPFound('/')
