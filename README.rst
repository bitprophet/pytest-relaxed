==============
pytest-relaxed
==============

``pytest-relaxed`` provides 'relaxed' test discovery for pytest.

It is the spiritual successor to https://pypi.python.org/pypi/spec, but is
built for ``pytest`` instead of ``nosetests``, and rethinks some aspects of
the design (such as a decreased emphasis on the display side of things.)


Rationale
=========

Has it ever felt strange to you that we put our tests in ``tests/``, then name
the files ``test_foo.py``, name the test classes ``TestFoo``, and finally
name the test methods ``test_foo_bar``? Especially when almost all of the code
inside of ``tests/`` is, well, *tests*?

This pytest plugin takes a page from the rest of Python, where you don't have
to explicitly note public module/class members, but only need to hint as to
which ones are private. By default, all files and objects pytest is told to
scan will be considered tests; to mark something as not-a-test, simply prefix
it with an underscore.


Relaxed discovery
=================

The "it's a test by default unless underscored" approach works for files::

    tests
	├── _util.py
	├── one_module.py
	└── another_module.py

It's applied to module members::

    def _helper():
        pass

    def one_thing():
        assert True

    def another_thing():
        assert False

    def yet_another():
        assert _helper() == 'something'

And to class members::

    class SomeObject:
        def behavior_one(self):
            assert True

        def another_behavior(self):
            assert False

        def _helper(self):
            pass

        def it_does_things(self):
            assert self._helper() == 'whatever'

Special cases
-------------

As you might expect, there are a few more special cases around discovery to
avoid fouling up common test extensions:

- Files named ``conftest.py`` aren't treated as tests, because they do special
  pytest things;
- Module and class members named ``setup_(module|class|method|function)`` are
  not considered tests, as they are how pytest implements classic/xunit style
  setup and teardown;
- Objects decorated as fixtures with ``@pytest.fixture`` are, of course,
  also skipped.


Nested class organization
=========================

On top of the relaxed discovery algorithm, ``pytest-relaxed`` also lets you
organize tests in a nested fashion, again like the ``spec`` nose plugin or the
tools that inspired it, such as Ruby's ``rspec``.

This is purely optional, but we find it's a nice middle ground between having a
proliferation of files or suffering a large, flat test namespace making it hard
to see which feature areas have been impacted by a bug (or whatnot).

The feature is enabled by using nested/inner classes, like so::

    class SomeObject:
        def basic_behavior(self):
            assert True

        class init:
            "__init__"

            def no_args_required(self):
                assert True

            def accepts_some_arg(self):
                assert True

            def sets_up_config(self):
                assert False

        class some_method:
            def accepts_whatever_params(self):
                assert False

            def base_behavior(self):
                assert True

            class when_config_says_foo:
                def it_behaves_like_this(self):
                    assert False

            class when_config_says_bar:
                def it_behaves_like_this(self):
                    assert True

Test discovery on these inner classes is recursive, so you *can* nest them as
deeply as you like. Naturally, as with all Python code, sometimes you can have
too much of a good thing...but that's up to you.

.. note::
    If writing Python-2-old-style classes makes you uncomfortable, you can
    write them as e.g. ``class SomethingUnderTest(object):`` - pytest-relaxed
    doesn't actually care. This is (naturally) moot under Python 3.


Installation & use
==================

As with most pytest plugins, it's dead simple:

- ``pip install pytest-relaxed``;
- Tell pytest where your tests live; otherwise pytest-relaxed will cause
  pytest to load all of your code as tests! We recommend using ``setup.cfg``
  or similar::

    [tool:pytest]
    testpaths = tests

- Write some tests, as exampled above;
- ``pytest`` to run the tests, and you're done!
