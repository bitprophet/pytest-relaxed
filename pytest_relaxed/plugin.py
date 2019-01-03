import pytest

from .classes import SpecModule
from .reporter import RelaxedReporter

# NOTE: fixtures must be present in the module listed under our setup.py's
# pytest11 entry_points value (i.e., this one.) Just being in the import path
# (e.g. package __init__.py) was not sufficient!
from .fixtures import environ  # noqa


def pytest_ignore_collect(path, config):
    # Ignore files and/or directories marked as private via Python convention.
    return path.basename.startswith("_")


def pytest_collect_file(path, parent):
    # Modify file selection to choose all .py files besides conftest.py.
    # (Skipping underscored names is handled up in pytest_ignore_collect, which
    # applies to directories too.)
    if (
        path.ext == ".py"
        and path.basename != "conftest.py"
        # Also skip anything prefixed with test_; pytest's own native
        # collection will get that stuff, and we don't _want_ to try modifying
        # such files anyways.
        and not path.basename.startswith("test_")
    ):
        # Then use our custom module class which performs modified
        # function/class selection as well as class recursion
        return SpecModule(path, parent)


@pytest.mark.trylast  # So we can be sure builtin terminalreporter exists
def pytest_configure(config):
    # TODO: we _may_ sometime want to do the isatty/slaveinput/etc checks that
    # pytest-sugar does?
    builtin = config.pluginmanager.getplugin("terminalreporter")
    # Pass the configured, instantiated builtin terminal reporter to our
    # instance so it can refer to e.g. the builtin reporter's configuration
    ours = RelaxedReporter(builtin)
    # Unregister the builtin first so only our output appears
    config.pluginmanager.unregister(builtin)
    config.pluginmanager.register(ours, "terminalreporter")
