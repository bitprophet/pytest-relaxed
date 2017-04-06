==============
pytest-relaxed
==============

``pytest-relaxed`` provides 'relaxed' test discovery for pytest.

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

    class SomeObject(object):
        def behavior_one(self):
            assert True

        def another_behavior(self):
            assert False

        def _helper(self):
            pass

        def it_does_things(self):
            assert self._helper() == 'whatever'

Exceptions
----------

As you might expect, there are a few more special cases around discovery to
avoid fouling up common test extensions:

- Files named ``conftest.py`` aren't treated as tests, because they do special
  pytest things;
- Module and class members named ``setup_(module|class|method|function)`` are
  not considered tests, as they are how pytest implements classic/xunit style
  setup and teardown;
- Objects decorated as fixtures with ``@pytest.fixture`` are, of course,
  also skipped.

Don't forget to specify where your tests live
---------------------------------------------

Relaxed discovery is predicated on keeping your tests in some obviously
namespaced directory structure - so make sure you inform pytest what that is,
or you'll find it attempting to load *all* of your code as tests!

Easiest is probably to use a config file like ``pytest.ini`` or ``setup.cfg``;
we like the latter, e.g.::

    [tool:pytest]
    testpaths = tests
