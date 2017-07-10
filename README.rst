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

Nested class attributes
-----------------------

If you're namespacing your tests via nested classes, you may find yourself
wanting to reference the enclosing "scope" of the outer classes they live in,
such as class attributes. pytest-relaxed automatically copies such attributes
onto inner classes during the test collection phase, allowing you to write code
like this::

    class Outer:
        behavior_one = True

        def outer_test(self):
            assert self.behavior_one

        class Inner:
            behavior_two = True

            def inner_test(self):
                assert self.behavior_one and self.behavior_two

Notably:

- The behavior is nested, infinitely, as you might expect;
- Attributes that look like test classes or methods themselves, are not copied
  (though others, i.e. ones named with a leading underscore, are);
- Only attributes _not_ already present on the inner class are copied; thus
  inner classes may naturally "override" attributes, just as with class
  inheritance.


Other test helpers
==================

``pytest-relaxed`` offers a few other random lightweight test-related utilities
that don't merit their own PyPI entries (most ported from ``spec``), such as:

- ``trap``, a decorator for use on test functions and/or test
  helpers/subroutines which is similar to pytest's own ``capsys``/``capfd``
  fixtures in that it allows capture of stdout/err.

    - It offers a slightly simpler API: it replaces ``sys.(stdout|stderr)`` with
      ``IO`` objects which can be ``getvalue()``'d as needed.
    - More importantly, it can wrap arbitrary callables, which is useful for
      code-sharing use cases that don't easily fit into the design of fixtures.

- ``raises``, a wrapper around ``pytest.raises`` which works as a decorator,
  similar to the Nose testing tool of the same name.


Nested output display
=====================

Continuing in the "port of ``spec`` / inspired by RSpec and friends" vein,
``pytest-relaxed`` greatly enhances pytest's verbose display mode:

- Tests are shown in a nested, tree-like fashion, with 'header' lines shown for
  modules, classes (including nested classes) and so forth.
- The per-test-result lines thus consist of just the test names, and are
  colorized (similar to the built-in verbose mode) based on
  success/failure/skip.
- Headers and test names are massaged to look more human-readable, such as
  replacing underscores with spaces.

*Unlike* ``spec``, this functionality doesn't affect normal/non-verbose output
at all, and can be disabled entirely, allowing you to use the relaxed test
discovery alongside normal pytest verbose display or your favorite pytest
output plugins (such as ``pytest-sugar``.)


Installation & use
==================

As with most pytest plugins, it's quite simple:

- ``pip install pytest-relaxed``;
- Tell pytest where your tests live via the ``testpaths`` option; otherwise
  pytest-relaxed will cause pytest to load all of your non-test code as tests!
- Not required, but **strongly recommended**: configure pytest's default
  filename pattern (``python_files``) to be an unqualified glob (``*``).

    - This doesn't impact (our) test discovery, but pytest's assertion
      'rewriting' (the feature that turns ``assert var == othervar`` into
      ``assert 17 == 2`` during error display) reuses this setting when
      determining which files to manipulate.

- Thus, a recommended ``setup.cfg`` (or ``pytest.ini``, sans the header) is::

    [tool:pytest]
    testpaths = tests
    python_files = *

- Write some tests, as exampled above;
- ``pytest`` to run the tests, and you're done!
