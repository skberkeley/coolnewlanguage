import collections.abc
from typing import List, Optional, Sequence, Iterable

import jinja2
import sqlalchemy
import json

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.input_component import InputComponent
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
    
    def append(self, other):
        from coolNewLanguage.src.cnl_type.link import Link
        from coolNewLanguage.src.cnl_type.cnl_type import CNLType
        from coolNewLanguage.src.component.user_input_component import UserInputComponent
        mapping = {}
        if self.value is None:
            raise ValueError("Cannot insert into UI table")
        match other:
            case CNLType():
                flatten_fields = CNLType._hls_type_to_field_flattening(other.__class__)
                columns = [n for (n, _) in flatten_fields.items()]
                for (field_name, field) in flatten_fields.items():
                    value = other.__getattribute__(field_name)
                    if value is None and not field.optional:
                        raise ValueError(f"Missing required field {field_name}")
                    if value is None or isinstance(value, Link):
                        # TODO: Maybe link fields should contain the link ID's
                        # I think right now they're just empty
                        continue
                    else:
                        # TODO: Delete this print
                        print(value)
                        integral_value = field.type(value)
                    mapping[field_name] = integral_value
                # TODO: Delete this print
                print(mapping)
                pass
            case dict():
                lifted = {}
                for (k, v) in other.items():
                    match v:
                        case UserInputComponent():
                            lifted[k] = v.expected_type(v.value)
                        case _:
                            lifted[k] = v
                mapping = lifted
            case _:
                raise TypeError("Cannot insert unknown type into table")
            
        insert_stmt = sqlalchemy.insert(self.value).values(mapping)
        with process.running_tool.db_engine.connect() as conn:
            conn.execute(insert_stmt)
            conn.commit()

    def delete(self):
        if self.value is None:
            raise ValueError("Cannot insert into UI table")
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
