from pytest import skip # noqa


# For 'testdir' fixture, mostly
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

    def skips_setup_and_teardown(self, testdir):
        # TODO: probably other special names we're still missing?
        testdir.makepyfile("""
            def setup():
                pass

            def teardown():
                pass

            def actual_test():
                pass

            class Outer:
                def setup(self):
                    pass

                def teardown(self):
                    pass

                def actual_nested_test(self):
                    pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        assert "::setup" not in stdout
        assert "::teardown" not in stdout
        assert "::actual_test" in stdout
        assert "::actual_nested_test" in stdout

class SpecModule:
    def skips_imported_names(self, testdir):
        testdir.makepyfile(_util="""
            def helper():
                pass
        """)
        testdir.makepyfile("""
            from _util import helper

            def a_test():
                pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        assert "::a_test" in stdout
        assert "::helper" not in stdout

    def replaces_class_tests_with_custom_recursing_classes(self, testdir):
        testdir.makepyfile("""
            class Outer:
                class Middle:
                    class Inner:
                        def oh_look_an_actual_test(self):
                            pass
        """)
        stdout = testdir.runpytest("-v").stdout.str()
        assert "Outer::Middle::Inner::oh_look_an_actual_test" in stdout


class SpecInstance:
    def methods_self_objects_exhibit_class_attributes(self, testdir):
        # Mostly a sanity test; pytest seems to get out of the way enough that
        # the test is truly a bound method & the 'self' is truly an instance of
        # the class.
        testdir.makepyfile("""
            class MyClass:
                an_attr = 5

                def some_test(self):
                    assert hasattr(self, 'an_attr')
                    assert self.an_attr == 5
        """)
        # TODO: first thought was "why is this not automatic?", then realized
        # "duh, it'd be annoying if you wanted to test failure related behavior
        # a lot"...but still want some slightly nicer helper I think
        assert testdir.runpytest().ret == 0

    def nested_self_objects_exhibit_parent_attributes(self, testdir):
        # TODO: really starting to think going back to 'real' fixture files
        # makes more sense; this is all real python code and is eval'd as such,
        # but it is only editable and viewable as a string. No highlighting.
        # TODO: downside is that presumably over many tests, the disk hit (even
        # on SSD??) might add up?
        testdir.makepyfile("""
            class MyClass:
                an_attr = 5

                class Inner:
                    def inner_test(self):
                        assert hasattr(self, 'an_attr')
                        assert self.an_attr == 5
        """)
        assert testdir.runpytest().ret == 0

    def nesting_is_infinite(self, testdir):
        testdir.makepyfile("""
            class MyClass:
                an_attr = 5

                class Inner:
                    class Deeper:
                        class EvenDeeper:
                            def innermost_test(self):
                                assert hasattr(self, 'an_attr')
                                assert self.an_attr == 5
        """)
        assert testdir.runpytest().ret == 0

    def overriding_works_naturally(self, testdir):
        testdir.makepyfile("""
            class MyClass:
                an_attr = 5

                class Inner:
                    an_attr = 7

                    def inner_test(self):
                        assert self.an_attr == 7
        """)
        assert testdir.runpytest().ret == 0

    def test_methods_from_outer_classes_are_not_copied(self, testdir):
        testdir.makepyfile("""
            class MyClass:
                def outer_test(self):
                    pass

                class Inner:
                    def inner_test(self):
                        assert not hasattr(self, 'outer_test')
        """)
        assert testdir.runpytest().ret == 0

    def module_contents_are_not_copied_into_top_level_classes(self, testdir):
        testdir.makepyfile("""
            module_constant = 17

            class MyClass:
                def outer_test(self):
                    assert not hasattr(self, 'module_constant')
        """)
        assert testdir.runpytest().ret == 0
