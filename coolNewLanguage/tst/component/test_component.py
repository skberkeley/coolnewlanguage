import pytest

from coolNewLanguage.src.component.component import Component
from coolNewLanguage.src.stage import config


class TestComponent:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        yield
        Component.num_components = 0
        config.component_list = []
        config.building_template = False

    def test_component_building_template_happy_path(self):
        # Setup
        config.building_template = True

        # Do
        component = Component()

        # Check
        assert component.component_id == 'component_0'
        assert component in config.component_list

    def test_component_not_building_template_happy_path(self):
        # Setup
        config.building_template = False

        # Do
        component = Component()

        # Check
        assert component.component_id == 'component_0'
        assert component not in config.component_list

    def test_component_paint(self):
        component = Component()
        # Do, Check
        with pytest.raises(NotImplementedError):
            component.paint()
