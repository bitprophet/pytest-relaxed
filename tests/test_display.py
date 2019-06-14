from pytest import skip

# Load some fixtures we expose, without actually loading our entire plugin
from pytest_relaxed.fixtures import environ  # noqa


# TODO: how best to make all of this opt-in/out? Reporter as separate plugin?
# (May not be feasible if it has to assume something about how our collection
# works?) CLI option (99% sure we can hook into that as a plugin)?


def _expect_regular_output(testdir):
    output = testdir.runpytest().stdout.str()
    # Regular results w/ status letters
    assert "behaviors.py .." in output
    assert "other_behaviors.py s.F." in output
    # Failure/traceback reporting
    assert "== FAILURES ==" in output
    assert "AssertionError" in output
    # Summary
    assert "== 1 failed, 4 passed, 1 skipped in " in output


class TestRegularFunctions:
    """
    Function-oriented test modules, normal display mode.
    """

    def test_acts_just_like_normal_pytest(self, testdir):
        testdir.makepyfile(
            behaviors="""
                def behavior_one():
                    pass

                def behavior_two():
                    pass
            """,
            other_behaviors="""
                from pytest import skip

                def behavior_one():
                    skip()

                def behavior_two():
                    pass

                def behavior_three():
                    assert False

                def behavior_four():
                    pass
            """,
        )
        _expect_regular_output(testdir)


class TestVerboseFunctions:
    """
    Function-oriented test modules, verbose display mode.
    """

    def test_displays_tests_indented_under_module_header(self, testdir):
        # TODO: at least, that seems like a reasonable thing to do offhand
        skip()

    def test_test_prefixes_are_stripped(self, testdir):
        testdir.makepyfile(
            legacy="""
            def test_some_things():
                pass

            def test_other_things():
                pass
        """
        )
        expected = (
            """
some things
other things
""".lstrip()
        )
        output = testdir.runpytest_subprocess("-v").stdout.str()
        assert expected in output


class TestNormalClasses:
    """
    Class-oriented test modules, normal display mode.
    """

    def acts_just_like_normal_pytest(self, testdir):
        testdir.makepyfile(
            behaviors="""
                class Behaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
            other_behaviors="""
                from pytest import skip

                class OtherBehaviors:
                    def behavior_one(self):
                        skip()

                    def behavior_two(self):
                        pass

                    def behavior_three(self):
                        assert False

                    def behavior_four(self):
                        pass
            """,
        )
        _expect_regular_output(testdir)


class TestVerboseClasses:
    """
    Class-oriented test modules, verbose display mode.
    """

    def test_shows_tests_nested_under_classes_without_files(self, testdir):
        testdir.makepyfile(
            behaviors="""
                class Behaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
            other_behaviors="""
                from pytest import skip
                class OtherBehaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        skip()

                    def behavior_three(self):
                        pass

                    def behavior_four(self):
                        assert False
            """,
        )
        output = testdir.runpytest_subprocess("-v").stdout.str()
        results = (
            """
Behaviors

    behavior one
    behavior two

OtherBehaviors

    behavior one
    behavior two
    behavior three
    behavior four
""".lstrip()
        )
        assert results in output
        # Ensure we're not accidentally nixing failure, summary output
        assert "== FAILURES ==" in output
        assert "AssertionError" in output
        # Summary
        assert "== 1 failed, 4 passed, 1 skipped in " in output

    def test_tests_are_colorized_by_test_result(  # noqa: F811,E501
        self, testdir, environ
    ):
        # Make sure py._io.TerminalWriters write colors despite pytest output
        # capturing, which would otherwise trigger a 'False' result for "should
        # markup output".
        environ["PY_COLORS"] = "1"
        testdir.makepyfile(
            behaviors="""
                class Behaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
            other_behaviors="""
                from pytest import skip
                class OtherBehaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        skip()

                    def behavior_three(self):
                        pass

                    def behavior_four(self):
                        assert False
            """,
        )
        output = testdir.runpytest_subprocess("-v").stdout.str()
        results = (
            """
Behaviors

    \x1b[32mbehavior one\x1b[0m
    \x1b[32mbehavior two\x1b[0m

OtherBehaviors

    \x1b[32mbehavior one\x1b[0m
    \x1b[33mbehavior two\x1b[0m
    \x1b[32mbehavior three\x1b[0m
    \x1b[31mbehavior four\x1b[0m
""".lstrip()
        )
        assert results in output
        # Ensure we're not accidentally nixing failure, summary output
        assert "== FAILURES ==" in output
        assert "AssertionError" in output
        # Summary
        assert "== 1 failed, 4 passed, 1 skipped in " in output

    def test_nests_many_levels_deep_no_problem(self, testdir):
        testdir.makepyfile(
            behaviors="""
                class Behaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass

                    class MoreBehaviors:
                        def an_behavior(self):
                            pass

                        def another_behavior(self):
                            pass

                    class YetMore:
                        class Behaviors:
                            def yup(self):
                                pass

                            def still_works(self):
                                pass
            """
        )
        expected = (
            """
Behaviors

    behavior one
    behavior two

    MoreBehaviors

        an behavior
        another behavior

    YetMore

        Behaviors

            yup
            still works
""".lstrip()
        )
        assert expected in testdir.runpytest("-v").stdout.str()

    def test_headers_and_tests_have_underscores_turn_to_spaces(self, testdir):
        testdir.makepyfile(
            behaviors="""
            class some_non_class_name_like_header:
                def a_test_sentence(self):
                    pass
        """
        )
        expected = (
            """
some non class name like header

    a test sentence
""".lstrip()
        )
        assert expected in testdir.runpytest("-v").stdout.str()

    def test_test_prefixes_are_stripped(self, testdir):
        testdir.makepyfile(
            stripping="""
            class TestSomeStuff:
                def test_the_stuff(self):
                    pass
        """
        )
        expected = (
            """
SomeStuff

    the stuff

""".lstrip()
        )
        assert expected in testdir.runpytest("-v").stdout.str()

    def test_test_suffixes_are_stripped(self, testdir):
        testdir.makepyfile(
            stripping="""
            class StuffTest:
                def test_yup(self):
                    pass
        """
        )
        expected = (
            """
Stuff

    yup

""".lstrip()
        )
        assert expected in testdir.runpytest("-v").stdout.str()


class TestNormalMixed:
    """
    Mixed function and class test modules, normal display mode.
    """

    # TODO: currently undefined; spec never even really worked for this
    pass


class TestVerboseMixed:
    """
    Mixed function and class test modules, verbose display mode.
    """

    # TODO: currently undefined; spec never even really worked for this
    pass
