from importlib.metadata import version


def get_version():
    """Get the current version of the tool"""
    return version("plsma")
