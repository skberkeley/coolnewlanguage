from unittest.mock import Mock

from coolNewLanguage.src.cnl_type.cnl_type import CNLType
from coolNewLanguage.src.cnl_type.field import Field

A_FIELD = Mock(spec=Field)
ANOTHER_FIELD = Mock(spec=Field)
YET_ANOTHER_FIELD = Mock(spec=Field)


class MyFirstType(CNLType):
    def fields(self) -> None:
        self.a_field = A_FIELD
        self.another_field = ANOTHER_FIELD
        self.yet_another_field = YET_ANOTHER_FIELD
