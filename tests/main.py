pytest_plugins = 'pytester'


# TODO: we don't actually _need_ new-style outer classes, do we...no Spec
# any longer!
# TODO: trailing underscore stripping
class FileCollection:
    def only_loads_dot_py_files(self, testdir):
        testdir.makepyfile(somefile="""
            def hello_how_are_you():
                pass
        """)
        testdir.makefile('.txt', someotherfile="whatever")
        stdout = testdir.runpytest("-v").stdout.str()
        # TODO: find it hard to believe pytest lacks strong "x in y" string
        # testing, but I cannot find any outside of fnmatch_lines (which is
        # specific to this testdir stuff, and also lacks an opposite...)
        assert "somefile.py::hello_how_are_you" in stdout
        # This wouldn't actually even happen; we'd get an ImportError instead
        # as pytest tries importing 'someotherfile'. But eh.
        assert "whatever.txt" not in stdout

    def skips_underscored_files(self, testdir):
        testdir.makepyfile(hastests="""
            from _util import helper

            def hello_how_are_you():
                helper()
        """)
        testdir.makepyfile(_util="""
            def helper():
                pass
        """)
        # TODO: why Result.str() and not str(Result)? Seems unPythonic
        stdout = testdir.runpytest("-v").stdout.str()
        assert "hastests.py::hello_how_are_you" in stdout
        assert "_util.py" not in stdout

    def does_not_consume_conftest_files(self, testdir):
        testdir.makepyfile(mytests="""
            def hello_how_are_you():
                pass
        """)
        testdir.makepyfile(conftest="""
            def this_does_nothing_useful():
                pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        assert "mytests.py::hello_how_are_you" in stdout
        assert "conftest.py" not in stdout
