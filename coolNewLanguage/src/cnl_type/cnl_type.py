from typing import Any, Optional, Union

from coolNewLanguage.src.cnl_type.field import Field
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.exceptions.CNLError import raise_type_casting_error
from coolNewLanguage.src.row import Row


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
        self._custom_fields: dict[str, Field] = {}
        # if we're initializing a subclass of CNLType, call fields
        if self.__class__ != CNLType:
            self.fields()

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
        instance of a Field to see whether it should be added to _custom_fields, then checks that _hls_backing_row is
        being overwritten with a non-Row object, then checks to see if a field's value is beign written to, before
        finally calling object.__set_attr
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
        elif hasattr(self, '_custom_fields') and name in self._custom_fields:
            self._custom_fields[name].set_value(value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, item: str) -> Any:
        """
        Override __getattr__ so that attribute references to programmer-defined fields are handled correctly. Tries to
        get the value from the value attribute on the Field object found in _custom_fields. If this value is None, tries
        to get it from this CNLType instance's _hls_backing_row, if that is present, setting it on the relevant Field
        object's value attribute before returning. If in that case _hls_backing_row is None, returns None instead. Since
        __getattr__ is called if __getattribute__ raises an AttributeError, only checks _custom_fields before raising an
        AttributeError itself
        :param item: The attribute name being accessed
        :return: The value of the Field being accessed, or None if the value of the Field is None and there is no
            backing_row present
        """
        custom_fields = self.__getattribute__('_custom_fields')

        if item not in custom_fields:
            raise AttributeError

        field = custom_fields[item]

        if field.value is not None:
            return field.value

        if self._hls_backing_row is None or item not in self._hls_backing_row:
            return None

        value = self._hls_backing_row[item]
        field.set_value(value)
        return value

    @staticmethod
    def CNL_type_to_fields(cnl_type: type['CNLType']) -> dict[str, Field]:
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

    @staticmethod
    def from_row(cnl_type: type['CNLType'], row: Row) -> 'CNLType':
        """
        Returns a new instance of the passed cnl_type backed by the passed Row instance. Checks to see that all the
        Fields defined by cnl_type are present in the row.
        :param cnl_type:
        :param row:
        :return:
        """
        if not issubclass(cnl_type, CNLType) or cnl_type is CNLType:
            raise TypeError("Expected cnl_type to be a strict subclass of CNLType")
        if not isinstance(row, Row):
            raise TypeError("Expected row to be a Row")

        cnl_type_instance = cnl_type()

        # Compare the expected fields and fields present in row
        for field_name in cnl_type_instance._custom_fields:
            if field_name not in row:
                raise_type_casting_error(
                    value=row,
                    expected_type=cnl_type,
                    error=ValueError("The Row did not contain all the expected fields")
                )

        cnl_type_instance._hls_backing_row = row

        return cnl_type_instance

    def link(self, link_dst: Union['Row', 'CNLType'], link_metatype: Link) -> Optional[int]:
        """
        Registers a link from this CNLType instance to link_dst, which is a Row or another CNLType instance. This method
        acts as a wrapper around the Row class's link method. However, it first checks to see if this instance has a
        backing row or not.
        :param link_dst:
        :param link_metatype:
        :return:
        """
        if self._hls_backing_row is None:
            return None

        return self._hls_backing_row.link(link_dst, link_metatype)

    def get_field_values(self) -> dict[str, Any]:
        """
        Returns a dictionary mapping programmer-defined attribute names to the values contained in the associated fields
        :return:
        """
        return {field_name: field.value for field_name, field in self._custom_fields.items() }