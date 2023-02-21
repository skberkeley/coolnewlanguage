from coolNewLanguage.src.stage import config


def get_component_id() -> str:
    """
    Get the id for the current component based on Component.num_components
    :return: The component id
    """
    return f'component_{Component.num_components}'


class Component:
    """
    Part of a stage's config

    Attributes:
        num_components:
            The number of components currently seen while either rendering
            the stage or handling the post request for the stage
            Used to set component id
            Since components are iterated over in the order in which they are
            defined within the stage function, this component id is guaranteed
            to be the same regardless of which time we are "initalizing" it
    """
    num_components = 0

    def __init__(self):
        """
        Initialize this component by setting its component id, incrementing
        num_components, and if currently building the Config template, paint
        this component and add it to the list of templates
        """
        self.component_id = get_component_id()
        Component.num_components += 1
        if config.building_template:
            config.template_list.append(self.paint())

    def paint(self):
        """
        Render this component as snippet of HTML. Not implemented for the base
        Component class
        :return:
        """
        raise NotImplementedError()
