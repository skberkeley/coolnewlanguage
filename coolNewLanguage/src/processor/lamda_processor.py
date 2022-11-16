from typing import Callable

from coolNewLanguage.src.processor.processor import Processor


class LambdaProcessor(Processor):
    def __init__(self, func: Callable):
        if not isinstance(func, Callable):
            raise TypeError("func of a LambdaProcessor should be a function")
        self.func = func

        if Processor.run_process:
            func()
