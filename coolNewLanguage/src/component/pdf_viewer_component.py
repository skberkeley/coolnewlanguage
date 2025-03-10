from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.models import UserContent


class PDFViewerComponent(Component):
    """
    A component used to display a PDF file
    Renders as an HTML embed tag
    """

    def __init__(self, user_content: UserContent):
        """
        Initialize this PDFViewerComponent
        :param user_content: The UserContent object containing the content details
        """
        if not isinstance(user_content, UserContent):
            raise TypeError("Expected user_content to be a UserContent object")

        self.user_content = user_content

        super().__init__()

    def paint(self) -> str:
        """
        Paint this PDFViewerComponent as a snippet of HTML
        :return: The painted PDFViewerComponent
        """
        return f'''
            <div>
                <h3>{self.user_content.content_name}</h3>
                <embed src="/pdf/{self.user_content.content_file_name}" type="application/pdf" width="100%" height="100%" />
            </div>
        '''
