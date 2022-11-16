from coolNewLanguage.src.stage.config import Config


def get_component_id():
    return f'component_{Component.num_components}'


class Component:
    num_components = 0

    def __init__(self):
        self.component_id = get_component_id()
        Component.num_components += 1
        if Config.building_template:
            Config.template_list.append(self.paint())

    def paint(self):
        pass
