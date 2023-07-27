from typing import Any, Type, Optional, Union

from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.cnl_type.link import Link


class CNLType:
    """
    CoolNewLanguageType
    A class designed to be subclasses by programmers so that they can define custom types
    Attributes:
        _hls_backing_row: Row : An optional Row object containing the underlying mapping for a particular CNLType
            instance, treated as a mapping between column names and values
        _custom_fields: Dict[str, Field] : A dictionary containing programmer defined fields corresponding to the
            attributes the programmer wants their custom type to have. Maps from the attribute name to the actual Field
            instance. Is used by __getattr__ and __setattr__.
    """
    __slots__ = ('_hls_backing_row', '_custom_fields')

    def __init__(self, backing_row: Optional['Row'] = None) -> None:
        from coolNewLanguage.src.row import Row

        if backing_row is not None and not isinstance(backing_row, Row):
            raise TypeError("Expected backing_row to be a Row")

        self._hls_backing_row = backing_row
        self._custom_fields = {}

    def fields(self) -> None:
        """
        fields is a placeholder within CNLType. Programmers subclassing CNLType to define custom types should override
        this method, defining the fields they want instances of their custom type to have within it.
        """
        msg = "The fields method is not defined for the CNLType parent class, and should be overwritten by its " \
              "subclasses"
        raise NotImplementedError(msg)

    def __setattr__(self, name: str, value: Union['Row', Field]):
        from coolNewLanguage.src.row import Row
        """
        Override __setattr__ so that attribute assignments made during calls to fields are handled, and attempts to
        overwrite _custom_fields fail. First checks to see if name is '_custom_fields' then checks to see if value is an
        instance of a Field to see whether it should be added to _custom_fields, otherwise calls the regular __setattr__
        method.
        :param name: The key to use for _custom_fields, or the name to assign to the attribute
        :param value: The value to pass to _custom_fields, or to set as the attribute
        :return:
        """
        if name == '_custom_fields' and hasattr(self, '_custom_fields'):
            raise AttributeError("Cannot overwrite attribute _custom_fields. Use another attribute name instead")
        elif name == '_hls_backing_row' and value is not None and not isinstance(value, Row):
            raise TypeError("Expected value to be a Row when assigning to attribute '_hls_backing_row'")
        elif isinstance(value, Field):
            self._custom_fields[name] = value
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, item: str) -> Field:
        """
        Override __getattr__ so that attribute references to programmer-defined fields are handled correctly. Since
        __getattr__ is called if __getattribute__ raises an AttributeError, only checks _custom_fields before raising
        an AttributeError itself
        :param item: The attribute name being accessed
        :return: The Field being accessed
        """
        custom_fields = self.__getattribute__('_custom_fields')
        if item in custom_fields:
            return custom_fields[item]
        raise AttributeError

    @staticmethod
    def _hls_type_to_fields(cnl_type: type['CNLType']):
        """
        Returns a dictionary containing the programmer-defined fields of the passed CNLType
        Instantiates a new objects and calls fields before accessing _custom_fields to figure out what the fields are
        :param cnl_type: A CNLType, either the base class itself or a subclass
        :return: A dictionary containing the programmer-defined fields of the passed CNLType
        """
        if not issubclass(cnl_type, CNLType):
            raise TypeError("Expected cnl_type to be a subclass of CNLType")

        cnl_type_instance: CNLType = cnl_type()
        cnl_type_instance.fields()
        return cnl_type_instance._custom_fields

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
