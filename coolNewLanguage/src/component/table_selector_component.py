import jinja2
import pandas as pd

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.stage import process, config


class TableSelectorComponent(InputComponent):
    NUM_PREVIEW_COLS = 5
    NUM_PREVIEW_ROWS = 5
    """
   A component used to list all tables and select one 

    Attributes:
        label: The label to paint onto this TableSelectorComponent
        template: The template to use to paint this TableSelectorComponent
        only_user_tables: Whether only user-created tables should be selectable or CNL-created metadata tables can also
            be selected
    """
    
    def __init__(self, label: str = "", only_user_tables: bool = True):
        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")
        if not isinstance(only_user_tables, bool):
            raise TypeError("Expected only_user_tables to be a boolean")

        self.label = label if label != "" else "Select table..."

        self.only_user_tables = only_user_tables

        super().__init__(expected_type=pd.DataFrame)

        # replace value with the chosen table's dataframe if handling post
        if process.handling_post:
            table_name = self.value
            self.value = process.running_tool.tables[table_name]

    def paint(self) -> str:
        """
        Paint this TextComponent as a snippet of HTML
        :return: The painted TableSelectorComponent
        """
        # Load the jinja template
        template: jinja2.Template = config.tool_under_construction.jinja_environment.get_template(
            name=consts.TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME
        )

        tool_tables = config.tool_under_construction.tables
        tables = []
        for i, table_name in enumerate(tool_tables.get_table_names()):
            tables.append(
                {
                    'name': table_name,
                    'cols': tool_tables.get_columns_of_table(table_name),
                    'rows': tool_tables[table_name].head(self.NUM_PREVIEW_ROWS),
                    'transient_id': i
                }
            )

        # Render and return the template
        return template.render(
            label=self.label,
            tables=tables,
            num_preview_cols=self.NUM_PREVIEW_COLS,
            component_id=self.component_id,
            context=consts.GET_TABLE_TABLE_SELECT
        )

    # def __iter__(self):
    #     if process.handling_post:
    #         return self.value.__iter__()
    #
    # def append(self, other: Union['CNLType', dict], get_user_approvals: bool = False) -> None:
    #     """
    #     Appends other as a row to the Table represented by this TableSelectorComponent by emitting an insert statement
    #     with values gathered from the other object. Assumes that the field names present in the CNLType or the keys in
    #     the dict exactly match the column names in this Table. If the value in a dict is a UserInputComponent instance,
    #     uses that Component's value attribute as the actual value to insert into this Table.
    #     :param other: Either a CNLType or a dict
    #     :param get_user_approvals: Whether to get user approvals before saving the append to the database
    #     :return:
    #     """
    #     from coolNewLanguage.src.cnl_type.cnl_type import CNLType
    #
    #     if not isinstance(other, CNLType) and not isinstance(other, dict):
    #         raise TypeError("Expected other to be a CNLType instance or a dictionary")
    #
    #     mapping = {}
    #
    #     if self.value is None:
    #         raise CNLError("Cannot append to a TableSelectorComponent outside of a Processor", Exception())
    #
    #     match other:
    #         case CNLType():
    #             other: CNLType
    #             mapping = other.get_field_values_with_columns()
    #         case dict():
    #             for k, v in other.items():
    #                 if k not in self.value.columns:
    #                     raise ValueError(f"Cannot append value to table for unknown column {k}")
    #                 if isinstance(v, InputComponent):
    #                     mapping[k] = v.value
    #                 else:
    #                     mapping[k] = v
    #         case _:
    #             raise TypeError("Cannot append unknown type onto table")
    #
    #     if get_user_approvals:
    #         from coolNewLanguage.src.approvals.row_approve_result import RowApproveResult
    #         table_name = self.value.name
    #         approve_result = RowApproveResult(row=mapping, table_name=table_name, is_new_row=True)
    #         process.approve_results.append(approve_result)
    #         return
    #
    #     insert_stmt = sqlalchemy.insert(self.value).values(mapping)
    #     with process.running_tool.db_engine.connect() as conn:
    #         conn.execute(insert_stmt)
    #         conn.commit()
    #
    # def delete(self):
    #     """
    #     Deletes the Table associated with this TableSelectorComponent
    #     :return:
    #     """
    #     if self.value is None:
    #         raise CNLError("Cannot delete a Table outside of a Processor", Exception())
    #
    #     self.value.drop(process.running_tool.db_engine)
