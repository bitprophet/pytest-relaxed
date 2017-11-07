=========
Changelog
=========

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
