from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.util.db_utils import *
from typing import List, Optional
import json


class ColumnSelectorComponent(InputComponent):
    """
    A linked, dependent component which allows a column to be selected 
    interactively based on a given selected table
    """
    def __init__(self, label: Optional[str] = None):
        self.table_selector: Optional['TableSelectorComponent'] = None
        if label and not isinstance(label, str):
            raise TypeError("Expected label to be a string")
        self.label = label if label else "Select column..."
        self.emulated_id:Optional[int] = None
        self.emulated_column:Optional[str] = None
        return super().__init__(expected_type=str)

    def _register_on_table_selector(self, table_selector: 'TableSelectorComponent'):
        if self.table_selector:
            raise AssertionError("Column must not be added to multiple table selectors")

        self.table_selector = table_selector

    def paint(self):
        # Column selectors are not painted by this object, they are owned and
        # painted by their respective TableSelector
        return ""

    def set(self, value):
        print("assign request", value)
        assign_column_value(
            tool=Process.running_tool,
            table_name=self.table_selector.value,
            column_name=self.emulated_column,
            column_id=self.emulated_id,
            value=value
        )

    def __lshift__(self, other):
        self.set(other)

    def __ilshift__(self, other):
        self.set(other)
        # By returning self, we can avoid destroying on assignment
        return self


class TableSelectorComponent(InputComponent):
    """
    A component used to list and select a single table 
    """
    
    def __init__(self, label: Optional[str] = None, columns: Optional[List[ColumnSelectorComponent]] = None):

        if label and not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        if columns:
            if not isinstance(columns, list):
                raise TypeError("Expected columns to be a list")
            if any([not isinstance(x, ColumnSelectorComponent) for x in columns]):
                raise TypeError("All column elements must be ColumnSelector")

        self.tool = Config.tool_under_construction
        self.label = label if label else "Select table..."
        self.template = self.tool.jinja_environment.get_template("table_selector.html")
        self.column_selectors: List[ColumnSelectorComponent] = columns if columns else []
        for column in self.column_selectors:
            column._register_on_table_selector(self)
        super().__init__(expected_type=str)

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        :return:
        """
        tables = get_tables(self.tool)
        table_column_map = {
            table: get_table_columns(self.tool, table)
            for table in tables
        }
        table_column_map_json = json.dumps(table_column_map)

        return self.template.render(
            component=self, 
            tables=tables,
            table_column_map_json=table_column_map_json, 
            column_selectors=self.column_selectors
        )
