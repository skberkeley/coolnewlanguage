from typing import List, Callable

from coolNewLanguage.src.component.table_selector import ColumnSelectorComponent
from coolNewLanguage.src.processor.processor import Processor
from coolNewLanguage.src.stage.process import Process
from coolNewLanguage.src.stage.stage import Stage
from itertools import product

from coolNewLanguage.src.util.db_utils import iterate_over_column


class ColumnXProductProcessor(Processor):
    """
    A processor which executes a lambda function passed to the Processor for
    every combination of the given columns
    """
    def __init__(self, columns: List[ColumnSelectorComponent], func: Callable):
        """
        Initialize this processor
        If handling a post request, run the passed func
        :param func: The lambda function to be run as part of the processor
        """

        if not isinstance(func, Callable):
            raise TypeError("func of a processor should be a function")
        if any([not isinstance(x, ColumnSelectorComponent) for x in columns]):
            raise TypeError("All column elements must be ColumnSelector")

        self.func = func

        if Stage.handling_post:
            iterators = [
                iterate_over_column(tool=Process.running_tool, table_name=c.table_selector.value, column_name=c.value)
                for c in columns
            ]
            
            # Stash the column string since we replace the proxy value
            for c in columns:
                c.emulated_column = c.value
            
            for entry in product(*iterators):
                for (column, data) in zip(columns, entry):
                    column.emulated_row_id = data[0]
                    column.value = data[1]
                func()
            self.result = None
        else:
            self.result = None
