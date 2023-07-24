import pathlib

import aiohttp.web_request
import jinja2

from coolNewLanguage.src import consts
from coolNewLanguage.src.component.input_component import InputComponent
from coolNewLanguage.src.stage import config


class FileUploadComponent(InputComponent):
    """
    A component used to accept user file uploads
    If handling a post request, write a copy of the uploaded file, and set this component's value to be the path to
    that copy
    expected_ext is enforced by the browser by adding an accept attribute to the input component
    """

    def __init__(self, expected_ext: str, label: str = ''):
        if not isinstance(expected_ext, str):
            raise TypeError("Expected expected_ext to be a string")
        if not isinstance(label, str):
            raise TypeError("Expected label to be a string")

        self.expected_ext = expected_ext
        self.label = label

        super().__init__(pathlib.Path)

        if self.value is not None:
            if not isinstance(self.value, aiohttp.web_request.FileField):
                raise TypeError("Expected value to be an aiohttp FileField")
            # if FILES_DIR doesn't exist, create it
            consts.FILES_DIR.mkdir(parents=True, exist_ok=True)
            # construct path
            file_path = consts.FILES_DIR.joinpath(self.value.filename)
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
        # Load the jinja template
        template: jinja2.Template = config.tool_under_construction.jinja_environment.get_template(
            name=consts.FILE_UPLOAD_COMPONENT_TEMPLATE_FILENAME
        )
        # Render and return the template
        return template.render(label=self.label, component_id=self.component_id, expected_ext=self.expected_ext)
