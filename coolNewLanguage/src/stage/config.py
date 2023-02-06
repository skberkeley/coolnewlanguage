class Config:
    """
    A class to hold state while constructing Configs
    Since state is not passed to each component as they are initialized,
    we put variables here so component __init__ functions know where to "find" them

    Attributes:
        template_list:
            A list of HTML elements which comprise this Config

        submit_component_added:
            Whether a submit component has been added to the template_list yet
            Programmers can add their own submit components to the Config, but
            if they don't, we automatically add one so that users have a way to
            submit their inputs

        building_template:
            Whether we're currently constructing a Config or not
            False when handling a post request
    """
    template_list = []
    submit_component_added = False
    building_template = False
