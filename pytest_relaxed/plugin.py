from .classes import SpecModule


def pytest_collect_file(path, parent):
    # Modify file selection to choose anything not private and not a conftest
    if (
        path.ext == '.py' and
        not path.basename.startswith('_') and
        path.basename != 'conftest.py'
    ):
        # Then use our custom module class which performs modified
        # function/class selection as well as class recursion
        return SpecModule(path, parent)
