from typing import List, Optional, Any
import json

from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.stage.config import Config
from coolNewLanguage.src.stage.process import Process
from coolNewLanguage.src.util.db_utils import update_cell, get_table_names_from_tool, get_column_names_from_table_name



class ColumnSelectorComponent(InputComponent):
    """
    A linked, dependent component which allows a column to be selected 
    interactively based on a given selected table

    If created before their associated TableSelectorComponent, ColumnSelectors must be passed as a list when the
    TableSelectorComponent is initialized.
    If created after their associated TableSelectorComponent, ColumnSelectors must:
        1. Have the register_on_table_selector(table) method called on the associated TableSelectorComponent
        2. Be appended to the TableSelectorComponent's columns attribute
    For convenience, the create_column_selector_from_table_selector can be used

    Attributes:
        table_selector: The TableSelector representing the table from which a column is being selected
        label: The label to paint onto this ColumnSelector
        emulated_row_id: The id of the row this selector currently represents, used when during execution of certain
            Processors
        emulated_column: The name of the column this selector represents
    """
    def __init__(self, label: Optional[str] = None):
        if label is not None and not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        self.table_selector: Optional['TableSelectorComponent'] = None
        self.label = label if label else "Select column..."
        self.emulated_row_id: Optional[int] = None
        self.emulated_column: Optional[str] = None
        return super().__init__(expected_type=str)

    def register_on_table_selector(self, table_selector: 'TableSelectorComponent'):
        """
        Register this ColumnSelector on a TableSelector to specify the table from which a column is being selected
        :param table_selector: The TableSelector representing the table from which a column is being selected
        :return: None
        """
        if not isinstance(table_selector, TableSelectorComponent):
            raise TypeError("Expected table_selector to be a TableSelectorComponent")
        if self.table_selector is not None:
            raise AssertionError("Column must not be added to multiple table selectors")

        self.table_selector = table_selector

    def paint(self):
        """
        Column selectors are not painted by ColumnSelectorComponents, instead they are painted by their registered
        TableSelectorComponents
        :return: ""
        """
        return ""
    
    def set(self, value: Any):
        """
        Overwrite the cell this ColumnSelectorComponent currently represents with value
        Note: This method overwrites data in the actual database, rather than changing a copy of the data this object
        has
        :param value: The value to update the cell with
        :return:
        """
        update_cell(tool=Process.running_tool, table_name=self.table_selector.value, column_name=self.emulated_column,
                    row_id=self.emulated_row_id, value=value)

    def __lshift__(self, other: Any):
        """
        Set the value of the cell this object is currently emulating to other
        Overloads the << operator
        c1 << c2 is equivalent to c1.__lshift__(c2) is equivalent to c1.set(c2)
        :param other: The value to update the cell with
        :return:
        """
        self.set(other)


class TableSelectorComponent(InputComponent):
    """
    A component used to list and select a single table

    Attributes:
        label: The label to paint onto this TableSelectorComponent
        template: The template to use to paint this TableSelectorComponent
        columns: A list of ColumnSelectorComponents, each of which select a column from the table associated with this
            TableSelectorComponent
    """
    
    def __init__(self, label: Optional[str] = None, columns: Optional[List[ColumnSelectorComponent]] = None):
        if label is not None and not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        if columns is not None:
            if not isinstance(columns, list):
                raise TypeError("Expected columns to be a list")
            if any([not isinstance(x, ColumnSelectorComponent) for x in columns]):
                raise TypeError("Each element of columns must be ColumnSelector")

        self.label = label if label else "Select table..."

        if Config.building_template:
            self.template = Config.tool_under_construction.jinja_environment.get_template('table_selector.html')

        self.columns: List[ColumnSelectorComponent] = columns if columns else []
        for column in self.columns:
            column.register_on_table_selector(self)

        super().__init__(expected_type=str)

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        Also paints the ColumnSelectorComponents in self.columns
        :return: The painted TableSelectorComponent
        """
        tool = Config.tool_under_construction
        tables = get_table_names_from_tool(tool)
        table_column_map = {
            table: get_column_names_from_table_name(tool, table)
            for table in tables
        }
        table_column_map_json = json.dumps(table_column_map)

        return self.template.render(
            component=self, 
            tables=tables,
            table_column_map_json=table_column_map_json, 
            column_selectors=self.columns
        )


def create_column_selector_from_table_selector(table: TableSelectorComponent, label: Optional[str] = None):
    """
    Create and return a new ColumnSelectorComponent associated with the passed TableSelectorComponent
    Intended as a convenience method to be used to create new ColumnSelectorComponents after the associated
    TableSelectorComponent has already been created.
    :param table: The TableSelectorComponent to register the new ColumnSelectorComponent on
    :param label: The optional label the created ColumnSelectorComponent will have
    :return: A newly created ColumnSelectorComponent registered on the TableSelectorComponent
    """
    if not isinstance(table, TableSelectorComponent):
        raise TypeError("Expected table to be a TableSelectorComponent")
    if label is not None and not isinstance(label, str):
        raise TypeError("Expected label to be a string")

    col = ColumnSelectorComponent(label)

    col.register_on_table_selector(table)
    table.columns.append(col)

    return col
