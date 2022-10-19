from coolNewLanguage.src.modules.Module import Module
from coolNewLanguage.src.util import ImportUtils


class TextModule(Module):
    def __init__(self, contents):
        super().__init__()
        self.contents = contents

    def render(self):
        if self.rendered:
            return
        if self.tool is None:
            raise ValueError(self.tool, "Can't render module without an associated Tool")

        views_module = ImportUtils.import_django_module(f'{self.tool.tool_name}.views')
        default_response = getattr(views_module, 'default_response')
        if default_response == "":
            default_response = self.contents
        else:
            default_response += "\n" + self.contents
        setattr(views_module, 'default_response', default_response)
