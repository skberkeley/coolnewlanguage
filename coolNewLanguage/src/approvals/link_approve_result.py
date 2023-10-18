from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.cnl_type.link import Link
from coolNewLanguage.src.util import html_utils


class LinkApproveResult(ApproveResult):
    __slots__ = ('link', 'link_html')

    def __init__(self, link: Link):
        if not isinstance(link, Link):
            raise TypeError("Expected link to be a Link")

        super().__init__()
        self.approve_result_type = ApproveResultType.LINK
        self.link_html = html_utils.html_of_link(link)
        self.link = link
