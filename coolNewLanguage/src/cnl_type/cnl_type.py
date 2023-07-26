from typing import Any, Type

from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.cnl_type.link import Link


class CNLType:
    __slots__ = ['_hls_backing_row']

    def __init__(self, backing_row: 'Row' = None) -> None:
        from coolNewLanguage.src.row import Row

        if not isinstance(backing_row, Row):
            raise TypeError("Expected backing_row to be a Row")

        self._hls_backing_row = backing_row

    def fields(self):
        msg = "The fields method is not defined for the CNLType parent class, and should be overwritten by its " \
              "subclasses"
        raise NotImplementedError(msg)

    # TODO: Add a __setattr__

    # def field_to_nested(self, __name:str):
    #     fields = Tool.__type_to_fields(self.__class__)
    #     if __name  fields:
    #     fields = Tool.__type_to_field_flattening(self.__class__)
    #     fields =

    def __getattr__(self, name: str) -> Any:
        # TODO: Rewrite
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self.__hls_backing_row[name]

    def _hls_type_to_fields(type:Type["CNLType"]):
        # TODO: Make this static with @staticmethod
        """
        Uses fact that calling fields() (which is implemented by the programmer when subclassing CNLType) adds new
        attributes to distinguish between programmer-added attributes and pre-existing field names
        :return:
        """
        # TODO: Rewrite (type is a builtin)
        # TODO: use is_subclass or something like that
        if not isinstance(type(), CNLType):
            raise TypeError("Expected a CNLType")
        instance = type()
        instance_fields_t0 = instance.__dict__.copy()
        instance.fields()
        instance_fields_t1 = instance.__dict__.copy()
        instance_fields = {
            k : v for k, v in instance_fields_t1.items()
            if k not in instance_fields_t0.keys()
        }

        return instance_fields

    def _hls_flatten_field(f: Field, hiearchical_name:str) -> dict:
        # TODO: Add static decorator
        # TODO: Combine this and _hls_type_to_field_flattening so we don't have to mutually recurse
        # TODO: Fix these two so we don't run into infinite recursion with mutually referential CNLTypes
        if isinstance(f.type(), CNLType):
            return CNLType._hls_type_to_field_flattening(f.type, hiearchical_name)
        else:
            return {hiearchical_name : f}

    def _hls_type_to_field_flattening(type:Type["CNLType"], hiearchical_name:str = None) -> dict:
        """
        :param hiearchical_name:
        :return:
        """
        # TODO: Change type name
        if not isinstance(type(), CNLType):
            raise TypeError("Expected a CNLType")

        instance_fields = CNLType._hls_type_to_fields(type)
        result = {}
        for (name, field) in instance_fields.items():
            h_name = f"{hiearchical_name}.{name}" if hiearchical_name else name
            result.update(CNLType._hls_flatten_field(field, h_name))
        return result

    def link(self, to:Any, on:"Link"):
        # TODO: to is union of row and cnltype
        # TODO: check types at beginning
        # TODO: better argument names?
        # TODO: Delete unused variables
        from coolNewLanguage.src.row import Row
        from coolNewLanguage.src.util.db_utils import link_create
        from coolNewLanguage.src.stage import process

        link_field = on._hls_internal_field
        link_id = on._hls_internal_link_id

        src_row_id:int = self.__hls_backing_row.row_id
        # src_table:int = self.__hls_backing_row.table.name
        dst_row_id:int
        dst_table:str
        if (isinstance(to, Row)):
            to:Row
            dst_row_id = to.row_id
            dst_table = to.table.name
        elif (isinstance(to, CNLType)):
            to:CNLType
            dst_row_id = to.__hls_backing_row.row_id
            dst_table = to.__hls_backing_row.table.name
        else:
            raise TypeError("Unexpected link target type")

        link = link_create(process.running_tool, link_id, src_row_id, dst_table, dst_row_id)
        # TODO: Delet this line?
        print("Created link", link)
