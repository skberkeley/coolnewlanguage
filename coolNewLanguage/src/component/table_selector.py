from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import *
from typing import List, Optional
import json

class ColumnSelector(InputComponent):
    """
    A linked, dependent component which allows a column to be selected 
    interactively based on a given selected table
    """
    def __init__(self, label:Optional[str] = None):
        self.table_selector:Optional['TableSelector'] = None
        if label and not isinstance(label, str):
            raise TypeError("Expected label to be a string")
        self.label = label if label else "Select column..."
        return super().__init__(expected_type=str)

    def _register_on_table_selector(self, table_selector:'TableSelector'):
        if self.table_selector:
            raise AssertionError("Column must not be added to multiple table selectors")

        self.table_selector = table_selector

    def paint(self):
        # Column selectors are not painted by this object, they are owned and
        # painted by their respective TableSelector
        return ""

class TableSelector(InputComponent):
    """
    A component used to list and select a single table 
    """
    
    def __init__(self, tool:Tool, label:Optional[str] = None, columns:Optional[List[ColumnSelector]]=None):
        if not isinstance(tool, Tool):
            raise TypeError("Expected a Tool for tool")

        if label and not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        if columns:
            if not isinstance(columns, list):
                raise TypeError("Expected columns to be a list")
            if any([not isinstance(x, ColumnSelector) for x in columns]):
                raise TypeError("All column elements must be ColumnSelector")

        self.tool = tool
        self.label = label if label else "Select table..."
        self.template = tool.jinja_environment.get_template("table_selector.html")
        self.column_selectors:List[ColumnSelector] = columns if columns else []
        super().__init__(expected_type=str)

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        :return:
        """
        tables = get_tables(self.tool)
        table_column_map = {
            table : get_table_columns(self.tool, table) 
            for table in tables
        }
        table_column_map_json = json.dumps(table_column_map)

        return self.template.render(
            component=self, 
            tables=tables,
            table_column_map_json=table_column_map_json, 
            column_selectors=self.column_selectors
        )

