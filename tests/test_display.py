from pytest import skip


# TODO: how best to make all of this opt-in/out? Reporter as separate plugin?
# (May not be feasible if it has to assume something about how our collection
# works?) CLI option (99% sure we can hook into that as a plugin)?


class TestNormalFunctions:
    """
    Function-oriented test modules, normal display mode.
    """
    def test_displays_tests_indented_under_module_header(self, testdir):
        # TODO: at least, that seems like a reasonable thing to do offhand
        skip()


class TestVerboseFunctions:
    """
    Function-oriented test modules, verbose display mode.
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
                def behavior_one():
                    pass

                def behavior_two():
                    pass
            """,
        )
        expected = "behaviors.py ..\nother_behaviors.py .."
        assert expected in testdir.runpytest().stdout.str()


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
                class OtherBehaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
        )
        expected = "behaviors.py ..\nother_behaviors.py .."
        assert expected in testdir.runpytest().stdout.str()


class TestVerboseClasses:
    """
    Class-oriented test modules, verbose display mode.
    """
    def test_shows_colorized_tests_nested_under_classes_without_files(
        self, testdir
    ):
        testdir.makepyfile(
            behaviors="""
                class Behaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
            other_behaviors="""
                class OtherBehaviors:
                    def behavior_one(self):
                        pass

                    def behavior_two(self):
                        pass
            """,
        )
        # TODO: ansi codes
        expected = """
Behaviors

    behavior_one
    behavior_two

OtherBehaviors

    behavior_one
    behavior_two
""".lstrip()
        assert expected in testdir.runpytest('-v').stdout.str()

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
            """,
        )
        # TODO: ansi codes
        expected = """
Behaviors

    behavior_one
    behavior_two

    MoreBehaviors

        an_behavior
        another_behavior

    YetMore

        Behaviors

            yup
            still_works
""".lstrip()
        assert expected in testdir.runpytest('-v').stdout.str()


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
