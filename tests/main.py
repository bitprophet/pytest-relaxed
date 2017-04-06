from pytest import skip # noqa


pytest_plugins = 'pytester'


class pytest_collect_file:
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
        testdir.makepyfile("""
            def hello_how_are_you():
                pass
        """)
        testdir.makepyfile(conftest="""
            def this_does_nothing_useful():
                pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        assert "::hello_how_are_you" in stdout
        assert "conftest.py" not in stdout


class RelaxedMixin:
    def selects_all_non_underscored_members(self, testdir):
        testdir.makepyfile("""
            def hello_how_are_you():
                pass

            def _help_me_understand():
                pass

            class YupThisIsTests:
                def please_test_me_thx(self):
                    pass

                def _helper_method_hi(self):
                    pass

                class NestedTestClassAhoy:
                    def hello_I_am_a_test_method(self):
                        pass

                    def _but_I_am_not(self):
                        pass

                class _NotSureWhyYouWouldDoThisButWhatever:
                    def this_should_not_appear(self):
                        pass

            class _ForSomeReasonIAmDefinedHereButAmNotATest:
                def usually_you_would_just_import_this_but_okay(self):
                    pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        for substring in (
            "hello_how_are_you",
            "please_test_me_thx",
            "hello_I_am_a_test_method",
        ):
            assert substring in stdout
        # TODO: if these or other 'assert x not in y' asserts fail, pytest is
        # _not_ displaying the values of either the substring or the stdout,
        # despite their website & demo claiming it will. Not sure what's
        # broken.
        for substring in (
            "_help_me_understand",
            "_helper_method_hi",
            "_NotSureWhyYouWouldDoThisButWhatever",
            "_ForSomeReasonIAmDefinedHereButAmNotATest",
        ):
            assert substring not in stdout
