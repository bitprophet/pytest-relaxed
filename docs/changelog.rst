=========
Changelog
=========

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
