from typing import Callable

from coolNewLanguage.src.processor.processor import Processor
from coolNewLanguage.src.stage import process


class LambdaProcessor(Processor):
    """
    A processor which executes a lambda function passed to the Processor
    """
    def __init__(self, func: Callable):
        """
        Initialize this LambdaProcessor
        If handling a post request, run the passed func
        :param func: The lambda function to be run as part of the processor
        """

        if not callable(func):
            raise TypeError("Expected func to be callable")
        self.func = func

        if process.handling_post:
            self.result = func()
        else:
            self.result = None
