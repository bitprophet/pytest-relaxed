import os

from pytest import fixture


# TODO: consider making this a "no param/funcarg required" fixture (i.e. one
# that gets decorated onto test classes instead of injected as magic kwargs)
# and have uses of it simply call os.environ as normal. Pro: test code looks
# less magical, con: removes any ability to do anything more interesting with
# the yielded value (like proxying or whatever.) See the pytest 3.1.2 docs at:
# /fixture.html#using-fixtures-from-classes-modules-or-projects
@fixture
def environ():
    """
    Enforce restoration of current shell environment after modifications.

    Yields the ``os.environ`` dict after snapshotting it; restores the original
    value (wholesale) during fixture teardown.
    """
    current_environ = os.environ.copy()
    yield os.environ
    os.environ = current_environ
