"""
A module to hold state while running Tools
Since some state isn't passed to processors as their tools run,
we put that state here so that it can be accessed

Attributes:
    running_tool: Tool
        The Tool currently being run
    handling_post: bool
        Whether a post request is currently being handled
        Used by other classes to determine current execution mode
    post_body: dict
        The body of the post request being handled
        Used by InputComponents to bind the results of input from users
    get_user_approvals: bool
        Whether the stage currently being processed is one that requires user approvals, in which case we cache changes
        to the db inside approve_results
    curr_stage_url: str
        The url of the stage currently being processed, used to generate the url which approval results are sent to
    approval_post_body: dict
        The body of the post request sent to the approval handler
        Used by the approval handler to determine which ApproveResults were approved and which were rejected
    cached_show_results: list[Result]
        A list of cached results to show, cached when get_user_approvals is set to True, since we get user approvals to
        determine the values which are actually committed to the db
    cached_show_results_title: str
        The title of the cached results to show
    handling_user_approvals: bool
        Whether the results of the user's approvals are currently being handled
"""
running_tool: 'Tool' = None
handling_post: bool = False
post_body: dict = None
get_user_approvals: bool = False
curr_stage_url: str = ""
approval_post_body: dict = None
cached_show_results: list['Result'] = []
cached_show_results_title: str = ""
handling_user_approvals: bool = False
