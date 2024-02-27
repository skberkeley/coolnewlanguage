from typing import Callable

from coolNewLanguage.src.processor.processor import Processor
from coolNewLanguage.src.stage import process


class LambdaProcessor(Processor):
    """
    A processor which executes a function passed to the Processor
    """
    def __init__(self, func: Callable, num_return_vals: int = 1):
        """
        Initialize this LambdaProcessor
        If handling a post request, run the passed func
        :param func: The lambda function to be run as part of the processor
        :param num_return_vals: The number of return values expected from func. Default 1
        """

        if not callable(func):
            raise TypeError("Expected func to be callable")
        self.func = func

        if process.handling_post:
            self.result = func()
        else:
            self.result = None

        self.num_return_vals = num_return_vals

    def __getattribute__(self, item):
        """
        Overrides __getattribute__ to support unpacking calls to this LambdaProcessor's result attribute when not handling
        post.
        :param item:
        :return:
        """
        if item == 'result' and not process.handling_post:
            return [None for _ in range(self.num_return_vals)]
        return object.__getattribute__(self, item)