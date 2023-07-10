import re


def check_has_only_alphanumerics_or_underscores(s: str) -> bool:
    """
    Checks whether the passed string contains only alphanumeric characters and underscores
    :param s:
    :return:
    """
    if not isinstance(s, str):
        raise TypeError("Expected s to be a string")
    return bool(re.fullmatch("[a-zA-Z0-9_]+", s))
