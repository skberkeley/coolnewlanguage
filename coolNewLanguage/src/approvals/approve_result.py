from coolNewLanguage.src.approvals.approve_state import ApproveState


class ApproveResult:
    num_approve_results = 0
    __slots__ = ('approve_state', 'approve_result_type', 'result_name', 'id')

    def __init__(self, result_name: str):
        self.result_name = result_name

        self.approve_state = ApproveState.PENDING

        self.id = ApproveResult.num_approve_results
        ApproveResult.num_approve_results += 1
