from invoke import task, Collection
from invocations.checks import blacken
from invocations.packaging import release
from invocations import docs, pytest as pytests, travis


@task
def coverage(c, html=True):
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
    if html:
        c.run("coverage html")
        c.run("open htmlcov/index.html")


# TODO: good candidate for builtin-to-invoke "just wrap <other task> with a
# tiny bit of behavior", and/or args/kwargs style invocations
@task
def test(
    c,
    verbose=True,
    color=True,
    capture="sys",
    opts="",
    x=False,
    k=None,
    module=None,
):
    """
    Run pytest with given options.

    Wraps ``invocations.pytests.test``. See its docs for details.
    """
    # TODO: could invert this & have our entire test suite manually _enable_
    # our own plugin, but given pytest's options around plugin setup, this
    # seems to be both easier and simpler.
    opts += " -p no:relaxed"
    pytests.test(
        c,
        verbose=verbose,
        color=color,
        capture=capture,
        opts=opts,
        x=x,
        k=k,
        module=module,
    )


ns = Collection(blacken, coverage, docs, test, travis, release)
ns.configure({"blacken": {"find_opts": "-and -not -path './build*'"}})
