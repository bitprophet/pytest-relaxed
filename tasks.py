from invoke import task, Collection
from invocations.packaging import release


# TODO: once this stuff is stable and I start switching my other projects to be
# pytest-oriented, move this into invocations somehow.
@task
def test(c):
    """
    Run verbose pytests.
    """
    c.run("pytest --verbose --color=yes")

@task
def coverage(c):
    """
    Run coverage with coverage.py.
    """
    # NOTE: this MUST use coverage itself, and not pytest-cov, because the
    # latter is apparently unable to prevent pytest plugins from being loaded
    # before pytest-cov itself is able to start up coverage.py! The result is
    # that coverage _always_ skips over all module level code, i.e. constants,
    # 'def' lines, etc. Running coverage as the "outer" layer avoids this
    # problem, thus no need for pytest-cov.
    # NOTE: this does NOT hold true for NON-PYTEST code, so
    # pytest-relaxed-USING modules can happily use pytest-cov.
    c.run("coverage run --source=pytest_relaxed -m pytest")
    c.run("coverage html")
    c.run("open htmlcov/index.html")


ns = Collection(
    coverage,
    test,
    packaging=release,
)
ns.configure({
})
