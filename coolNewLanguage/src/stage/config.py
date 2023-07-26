from typing import List

from coolNewLanguage.src.component.component import Component

"""
A module to hold state while constructing Configs
Since state is not passed to each component as they are initialized,
we put variables here so component __init__ functions know where to "find" them

Attributes:
    template_list:
        A list of HTML elements which comprise this Config
        
    component_list:
        A list of components, which one painted, will comprise the Config being constructed

    submit_component_added:
        Whether a submit component has been added to the template_list yet
        Programmers can add their own submit components to the Config, but
        if they don't, we automatically add one so that users have a way to
        submit their inputs

    building_template:
        Whether we're currently constructing a Config or not
        False when handling a post request

    tool_under_construction: Tool
        The Tool whose config is currently being constructed
"""

component_list: List[Component] = []
submit_component_added: bool = False
building_template: bool = False
tool_under_construction: 'Tool' = None
