from enum import Enum


class ApproveResultType(Enum):
    TABLE = "Table"
    ROW = "Row"
    LINK = "Link"
    TABLE_DELETION = "Table Deletion"
