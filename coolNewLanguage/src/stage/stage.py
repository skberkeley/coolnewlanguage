import urllib.parse
from typing import Callable

import jinja2
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.component.submit_component import SubmitComponent
from coolNewLanguage.src.stage import process, config


class Stage:
    """
    A stage of a data processing tool
    Provides two endpoints for the associated Tool's webapp
    handle provides the initial endpoint when the stage is first viewed, and returns the stage's Config, which it
    renders when the request is made
    post_handler provides the endpoint when the input from Config is submitted and handles processing data correctly and
    displaying any results

    Attributes:
        results_template:
            The rendered Jinja template containing any relevant results
            Set here by show_results() so that we have access to it outside the scope of the stage_func call
    """
    approvals_template: str = None
    results_template: str = None

    def __init__(self, name: str, stage_func: Callable):
        """
        Initialize this stage. The stage url is generated from the passed name
        :param name: This stage's name. Cannot begin with an underscore
        :param template: The pre-rendered template for this stage's Config
        :param stage_func: The function used to define this stage
        """
        if not isinstance(name, str):
            raise TypeError("Expected name to be a string")
        if name.startswith('_'):
            raise ValueError("Stage names cannot begin with underscores")
        self.name = name

        if not callable(stage_func):
            raise TypeError("Expected stage_func to be callable")
        self.stage_func = stage_func

        self.url = urllib.parse.quote(name)

    async def handle(self, request: web.Request) -> web.Response:
        """
        Handles get request for this stage by painting this stage and returning the rendered template
        :param request:
        :return:
        """
        template = self.paint()
        return web.Response(body=template, content_type=consts.AIOHTTP_HTML)

    def paint(self) -> str:
        """
        Returns the rendered Jinja template for this stage
        Begins by running stage_func to build a list of all the components to be included
        Then builds a list of all the painted components, which are then ready to be put into the Jinja template
        Finally, uses Jinja magic to render the HTML document using the template found at stage.html
        :return:
        """
        config.submit_component_added = False
        config.building_template = True
        config.tool_under_construction = process.running_tool
        # num_components is used for id's in the HTML template
        Component.num_components = 0

        # call the stage_func, so that each component adds itself to config.component_list
        self.stage_func()

        if not config.submit_component_added:
            SubmitComponent("Submit")

        painted_components = []
        for component in config.component_list:
            painted_comp = component.paint()
            if painted_comp is not None:
                painted_components.append(painted_comp)

        config.tool_under_construction = None
        config.building_template = False
        config.component_list = []

        # reset num_components
        Component.num_components = 0

        # load the jinja template
        template: jinja2.Template = process.running_tool.jinja_environment.get_template(
            name=consts.STAGE_TEMPLATE_FILENAME
        )
        # return the rendered template
        form_action = f'/{self.url}/post'
        form_method = 'post'
        return template.render(
            stage_name=self.name,
            form_action=form_action,
            form_method=form_method,
            component_list=painted_components
        )

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
        if not isinstance(request, web.Request):
            raise TypeError("Expected request to be a web Request")

        process.post_body = await request.post()
        process.handling_post = True
        Component.num_components = 0
        process.curr_stage_url = self.url
        process.cached_show_results_title = ""
        process.cached_show_results = []

        process.approve_results = []
        process.approval_post_body = None
        ApproveResult.num_approve_results = 0

        self.stage_func()

        process.post_body = None
        process.handling_post = False
        Component.num_components = 0
        process.curr_stage_url = ""

        # If process.get_user_approvals is set to True, redirect to the approvals page
        if process.get_user_approvals:
            template = Stage.approvals_template
            Stage.approvals_template = None
            return web.Response(body=template, content_type=consts.AIOHTTP_HTML)

        # Flush changes cached in the running tool's Tables instance
        process.running_tool.tables._flush_changes()

        # If the results template is set, redirect to that
        if Stage.results_template is not None:
            template = Stage.results_template
            Stage.results_template = None

            return web.Response(body=template, content_type=consts.AIOHTTP_HTML)
        # Else redirect to the home page
        raise web.HTTPFound('/')
