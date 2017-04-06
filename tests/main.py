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
        assert "whatever.txt" not in stdout
