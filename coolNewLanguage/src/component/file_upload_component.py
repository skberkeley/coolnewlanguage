from pathlib import Path

from aiohttp.web_request import FileField

from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.consts import FILES_DIR


class FileUploadComponent(InputComponent):
    """
    A component used to accept user file uploads
    If handling a post request, write a copy of the uploaded file, and set this component's value to be the path to
    that copy
    """

    def __init__(self, expected_ext: str, label: str = ''):
        if not isinstance(expected_ext, str):
            raise TypeError("Expected a string for expected extension")
        if not isinstance(label, str):
            raise TypeError("Expected a string for label")

        self.expected_ext = expected_ext
        self.label = label

        super().__init__(Path)

        if self.value is not None:
            if not isinstance(self.value, FileField):
                raise TypeError("Expected this file upload component's value to be an aiohttp FileField")
            # if FILES_DIR doesn't exist, create it
            FILES_DIR.mkdir(parents=True, exist_ok=True)
            # construct path
            file_path = FILES_DIR.joinpath(self.value.filename)
            # write our own copy of the file
            with open(file_path, mode='wb') as f:
                f.write(self.value.file.read())
            # set this value to be the relative path to that file
            self.value.file.close()
            self.value = file_path

    def paint(self) -> str:
        """
        Paint this FileUploadComponent as a snippet of HTML
        :return:
        """
        snippets = ['<div>']

        if self.label:
            snippets.append(f'<label for="{self.component_id}">{self.label}</label>')
            snippets.append('<br>')

        # file upload element
        snippets.append(
            f'<input type="file" id="{self.component_id}" name="{self.component_id}" accept="{self.expected_ext}" />'
        )

        snippets.append('</div>')

        return ''.join(snippets)
