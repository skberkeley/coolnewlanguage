import importlib
from types import ModuleType


def import_django_module(module_path, invalidate_caches=True) -> ModuleType:
    """
    Helper to import django module
    Invalidates caches to allow import of modules created at runtime
    :param module_path: Dot path to Django module to import
    :param invalidate_caches: Whether to invalidate caches or not
    :return: Imported module
    """
    if invalidate_caches:
        importlib.invalidate_caches()
    return importlib.import_module(module_path)
