class Process:
    """
    A class to hold state while running Tools
    Since some state isn't passed to processors as their tools run,
    we put that state here so that it can be accessed

    Attributes:
        running_tool: Tool
            The Tool currently being run
    """
    running_tool: 'Tool' = None
