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
