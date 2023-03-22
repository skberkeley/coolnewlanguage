from typing import Callable

import sqlalchemy

from coolNewLanguage.src.component.table_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.processor.processor import Processor
from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util.db_utils import update_column


class MapProcessor(Processor):
    """
    A processor which maps a function onto a column, updating its values as it goes
    """
    def __init__(self, col: ColumnSelectorComponent, func: Callable):
        """
        Initialize this MapProcessor
        If handling a post request, run the passed function on each value in col, updating col as it does
        :param col: The ColumnSelectorComponent representing the column to map onto
        :param func: The function to run on each value
        """
        if not isinstance(col, ColumnSelectorComponent):
            raise TypeError("Expected col to be a ColumnSelectorComponent")
        if not isinstance(func, Callable):
            raise TypeError("Expected func to be a function")

        if not process.handling_post:
            return

        # compute vals and get row ids
        row_id_and_vals = [(c.row_id, func(c)) for c in col]
        # issue update statement
        update_column(tool=process.running_tool, table=col.table_selector.value, col_name=col.emulated_column,
                      row_id_val_pairs=row_id_and_vals)
