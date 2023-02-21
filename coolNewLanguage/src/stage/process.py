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
"""
running_tool: 'Tool' = None
handling_post: bool = False
post_body: dict = None
