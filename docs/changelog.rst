=========
Changelog
=========

- :release:`2.0.2 <2024-03-29>`
- :bug:`32` Fix dangling compatibility issues with pytest version 8.x. Thanks
  to Alex Gaynor for the patch!
- :release:`2.0.1 <2023-05-22>`
- :bug:`9` Don't try loading Pytest fixture functions as if they were test
  functions. Classifying this as a bug even though it's a moderately sized
  change in behavior; it's vanishingly unlikely anybody was relying on this
  somehow! Thanks to ``@cajopa`` for the report.
- :release:`2.0.0 <2022-12-31>`
- :bug:`- major` Prior to version 2, we failed to correctly support true Pytest
  setup/teardown methods (i.e. ``setup_method`` and ``teardown_method``) and
  these would not get copied to inner class scopes. This has been fixed. We
  still support old nose-style ``setup``/``teardown`` for now, despite them
  going away in Pytest 8.
- :support:`-` Modernize codebase/project a bunch:

  - Dropped support for Python <3.6 (including 2.7)
  - Pytest support upgraded to support, **and require**, Pytest >=7.

    - This plugin never worked on Pytests 5 and 6 anyways, and supporting 5-7
      appears to require a lot more effort than just 7.

  - Behavioral changes in Pytest internals have fixed a handful of sorta-bugs
    present in pytest-relaxed under Pytest versions 3 and 4:

    - The order of nested test display may change slightly, typically for the
      better; eg under older versions, tests defined on a class might have been
      displayed after subclasses/nested tests - now they're more likely to be
      listed first, which was the original intent.
    - These bugs sometimes enabled "state bleed", such as outer scopes
      appearing to grant inner ones attributes set at runtime (eg by the outer
      scope's ``setup``, even when the inner scope redefined ``setup``).

      - If you encounter odd bugs after upgrading, please take a close look at
        your code and make sure you weren't accidentally using such a
        "feature". One good way to test for this is to run the "newly failing"
        tests by themselves on the old dependencies -- they will likely also
        fail there.

- :release:`1.1.5 <2019-06-14>`
- :bug:`2` Fix compatibility with pytest versions 3.3 and above.
- :release:`1.1.4 <2018-07-24>`
- :release:`1.0.2 <2018-07-24>`
- :support:`- backported` Add missing universal wheel indicator in setup
  metadata.
- :release:`1.1.3 <2018-07-24>`
- :release:`1.0.1 <2018-07-24>`
- :bug:`-` Fix the ``@raises`` helper decorator so it actually raises an
  exception when the requested exception is not raised by the decorated
  function. That's definitely not a confusing sentence.
- :release:`1.1.2 <2018-04-16>`
- :bug:`-` Neglected to update setup metadata when setting up a tiny Read The
  Docs instance. Homepage link now fixed!
- :release:`1.1.1 <2018-04-16>`
- :bug:`-` Installation and other ``setup.py`` activities implicitly assumed
  native Unicode support due to naively opening ``README.rst``. ``setup.py`` now
  explicitly opens that file with a ``utf-8`` encoding argument. Thanks to
  Ondřej Súkup for catch & patch.
- :bug:`-` Bypass ``pytestmark`` objects and attributes during our custom
  collection phase; we don't need to process them ourselves, pytest is already
  picking up the original top level copies, and having them percolate into
  nested classes was causing loud pytest collection-step warnings.
- :release:`1.1.0 <2017-11-21>`
- :feature:`-` Add support for collecting/displaying hybrid/legacy test suites
  -- specifically, by getting out of pytest's way on collection of
  ``test_named_files`` and stripping test prefixes/suffixes when displaying
  tests in verbose mode. This makes it easier to take an existing test suite
  and slowly port it to 'relaxed' style.
- :release:`1.0.0 <2017-11-06>`
- :support:`-` Drop Python 2.6 and 3.3 support.
- :feature:`-` Implement early drafts of Spec-like nested test display (which
  fires only when verbose output is enabled, unlike Spec which completely took
  over all output of nosetests.)
- :support:`-` Revert internal tests to *not* eat our own dogfood; typical TDD
  lifecycles don't work very well when partly-implemented new features cause
  all of the older tests to fail as well!
- :feature:`-` Create a ``@raises`` decorator which wraps ``pytest.raises``
  (we're not sure why it's not natively offered as a decorator!) and thus ends
  up appearing very similar to Nose's API member of same name.
- :feature:`-` Port ``@trap`` from Spec as it's currently a lot more natural to
  use than pytest's builtin capture fixtures. May back it out again later if
  we can make better sense of the latter / fit it into how our existing suites
  are organized.
- :support:`-` Basic Travis and CodeCov support.
- :bug:`- major` Various and sundry bugfixes, including "didn't skip
  underscore-named directories."
- :release:`0.1.0 <2017-04-08>`
- :feature:`-` Early draft functionality (test discovery only; zero display
  features.) This includes "releases" 0.0.1-0.0.4.
