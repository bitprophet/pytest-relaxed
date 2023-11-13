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


# We need to use collect_file, not pycollect_makemodule, as otherwise users
# _must_ specify a config blob to use us, vs that being optional.
# TODO: otoh, I personally use it all the time and we "strongly recommend it"
# so maybe find a way to make that config bit default somehow (update
# docs/changelog appropriately), and then switch  hooks?
def pytest_collect_file(file_path, parent):
    # Modify file selection to choose all .py files besides conftest.py.
    # (Skipping underscored names is handled up in pytest_ignore_collect, which
    # applies to directories too.)
    if (
        file_path.suffix != ".py"
        or file_path.name == "conftest.py"
        # Also skip anything prefixed with test_; pytest's own native
        # collection will get that stuff, and we don't _want_ to try modifying
        # such files anyways.
        or file_path.name.startswith("test_")
    ):
        return
    # Then use our custom module class which performs modified
    # function/class selection as well as class recursion
    return SpecModule.from_parent(parent=parent, path=file_path)


@pytest.hookimpl(trylast=True)  # Be sure builtin terminalreporter exists
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
