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
