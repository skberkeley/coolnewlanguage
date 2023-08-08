import collections.abc
from typing import List, Optional, Sequence, Iterable, Union

import jinja2
import sqlalchemy
import json

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.exceptions.CNLError import CNLError
from coolNewLanguage.src.row import Row
from coolNewLanguage.src.stage import process, config
from coolNewLanguage.src.util.db_utils import get_table_names_from_tool, get_column_names_from_table_name, \
    get_rows_of_table


class TableSelectorComponent(InputComponent):
    """
    A component used to list and select a single table

    Attributes:
        label: The label to paint onto this TableSelectorComponent
        template: The template to use to paint this TableSelectorComponent
        columns: A list of ColumnSelectorComponents, each of which select a column from the table associated with this
            TableSelectorComponent
    """
    
    def __init__(self, label: str = "", columns: List[ColumnSelectorComponent] = None):
        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        if columns is not None:
            if not isinstance(columns, list):
                raise TypeError("Expected columns to be a list")
            if any([not isinstance(x, ColumnSelectorComponent) for x in columns]):
                raise TypeError("Expected each element of columns to be a ColumnSelectorComponent")

        self.label = label if label != "" else "Select table..."

        if config.building_template:
            self.template: jinja2.Template = config.tool_under_construction.jinja_environment.get_template(
                consts.TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME
            )

        self.columns: List[ColumnSelectorComponent] = columns if columns is not None else []
        for column in self.columns:
            column.register_on_table_selector(self)

        super().__init__(expected_type=str)

        # replace value with an actual sqlalchemy Table object if handling post
        if process.handling_post:
            table_name = self.value
            self.value = sqlalchemy.Table(table_name, process.running_tool.db_metadata_obj)
            insp: sqlalchemy.engine.reflection.Inspector = sqlalchemy.inspect(process.running_tool.db_engine)
            # Pass None for include_columns to reflect all columns
            insp.reflect_table(table=self.value, include_columns=None)

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        Also paints the ColumnSelectorComponents in self.columns
        :return: The painted TableSelectorComponent
        """
        tool = config.tool_under_construction
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

    class TableSelectorIterator:
        def __init__(self, table: sqlalchemy.Table, rows: Iterable[sqlalchemy.Row]):
            if not isinstance(table, sqlalchemy.Table):
                raise TypeError("Expected table to be a sqlalchemy Table")
            if not isinstance(rows, collections.abc.Iterable):
                raise TypeError("Expected rows to be iterable")
            if not all([isinstance(r, sqlalchemy.Row) for r in rows]):
                raise TypeError("Expected every item in rows to be a sqlalchemy Row")

            self.table = table
            self.rows_iterator = rows.__iter__()

        def __next__(self) -> Row:
            try:
                sql_alchemy_row = self.rows_iterator.__next__()
            except StopIteration:
                raise StopIteration

            return Row(table=self.table, sqlalchemy_row=sql_alchemy_row)

    def __iter__(self):
        rows: Sequence[sqlalchemy.Row] = get_rows_of_table(process.running_tool, self.value)
        return TableSelectorComponent.TableSelectorIterator(table=self.value, rows=rows)
    
    def append(self, other: Union['CNLType', dict]) -> None:
        """
        Appends other as a row to the Table represented by this TableSelectorComponent by emitting an insert statement
        with values gathered from the other object. Assumes that the field names present in the CNLType or the keys in
        the dict exactly match the column names in this Table. If the value in a dict is a UserInputComponent instance,
        uses that Component's value attribute as the actual value to insert into this Table.
        :param other: Either a CNLType or a dict
        :return:
        """
        from coolNewLanguage.src.cnl_type.cnl_type import CNLType
        from coolNewLanguage.src.component.user_input_component import UserInputComponent

        if not isinstance(other, CNLType) and not isinstance(other, dict):
            raise TypeError("Expected other to be a CNLType instance or a dictionary")

        mapping = {}

        if self.value is None:
            raise CNLError("Cannot append to a TableSelectorComponent outside of a Processor", Exception())

        match other:
            case CNLType():
                other: CNLType
                mapping = other.get_field_values()
            case dict():
                for k, v in other.items():
                    if isinstance(v, InputComponent):
                        mapping[k] = v.value
                    else:
                        mapping[k] = v
            case _:
                raise TypeError("Cannot append unknown type onto table")
            
        insert_stmt = sqlalchemy.insert(self.value).values(mapping)
        with process.running_tool.db_engine.connect() as conn:
            conn.execute(insert_stmt)
            conn.commit()

    def delete(self):
        """
        Deletes the Table associated with this TableSelectorComponent
        :return:
        """
        if self.value is None:
            raise CNLError("Cannot delete a Table outside of a Processor", Exception())

        self.value.drop(process.running_tool.db_engine)


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
