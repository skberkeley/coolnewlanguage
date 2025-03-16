from enum import Enum


class ApproveResultType(Enum):
    TABLE = "Table"
    ROW = "Row"
    LINK = "Link"
    TABLE_DELETION = "Table Deletion"
    TABLE_SCHEMA_CHANGE = "Table Schema Change"
    TABLE_ROW_ADDITION = "Table Row Addition"
