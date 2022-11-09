from typing import List

from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.component.submit_component import SubmitComponent


class Config:
    def __init__(self, components: List[Component], submit_text: str = ""):
        if not all([isinstance(c, Component) for c in components]):
            raise TypeError("Every component of a Config should be of type Component")
        self.components = components
        self.components.append(SubmitComponent(submit_text=submit_text))

    def __iter__(self):
        return self.components.__iter__()
