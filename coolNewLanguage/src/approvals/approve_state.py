from enum import Enum, auto


class ApproveState(Enum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()

    @staticmethod
    def of_string(s: str):
        if s == "approve":
            return ApproveState.APPROVED
        elif s == "reject":
            return ApproveState.REJECTED
        elif s == "pending":
            return ApproveState.PENDING
        raise ValueError("Unrecognized ApproveState string: " + s)