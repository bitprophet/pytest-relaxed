from _pytest.terminal import TerminalReporter


# TODO:
# - how can we be sure the tests are in the right order?
#   - aka how can we 'sort' them? in post-collection step?
# - how to handle display of 'header' lines? Probably state tracking as w/
# spec?
# - how to deal with flat modules vs nested classes?
# - would be nice to examine all tests in a tree, but that requires waiting
# till all results are in, which is no bueno. So we really do just need to
# ensure a tree-based sort (which, assuming solid test ID strings, can be a
# lexical sort.)
#   - sadly, what this means is that the parent/child relationship between test
#   objects doesn't really help us any, since we have to take action on a
#   per-report basis. Meh. (guess if we NEEDED to access attributes of a parent
#   in a child, that'd be possible, but...seems unlikely-ish? Maybe indent
#   based on parent relationships instead of across-the-run state tracking?)


# NOTE: much of the high level "replace default output bits" approach is
# cribbed directly from pytest-sugar at 0.8.0
class RelaxedReporter(TerminalReporter):
    def __init__(self, builtin):
        # Pass in the builtin reporter's config so we're not redoing all of its
        # initial setup/cli parsing/etc. NOTE: TerminalReporter is old-style :(
        TerminalReporter.__init__(self, builtin.config)
        # Which headers have already been displayed
        # TODO: faster data structure probably wise
        self.headers_displayed = []
        # Size of indents. TODO: configuration
        self.indent = ' ' * 4

    def pytest_runtest_logstart(self, nodeid, location):
        # Non-verbose: do whatever normal pytest does.
        if not self.verbosity:
            return TerminalReporter.pytest_runtest_logstart(
                self, nodeid, location,
            )
        # Verbose: do nothing, preventing normal display of test location/id.
        # Leaves all display up to other hooks.

    def pytest_runtest_logreport(self, report):
        # TODO: if we _need_ access to the test item/node itself, we may want
        # to implement pytest_runtest_makereport instead? (Feels a little
        # 'off', but without other grody hax, no real way to get the obj so...)

        # Non-verbose: do whatever normal pytest does.
        # TODO: kinda want colors & per-module headers/indent though...
        if not self.verbosity:
            return TerminalReporter.pytest_runtest_logreport(self, report)
        # Verbose: this is our best opportunity to display new output on a
        # per-test basis (vs waiting until entire run is done.)
        # First, do nothing if it's not reporting the main call (i.e. we don't
        # want to display "the test" during its setup or teardown)
        if report.when != 'call':
            return
        id_ = report.nodeid
        # First, make sure we display non-per-test data, i.e.
        # module/class/nested class headers (which by necessity also includes
        # tracking indentation state.)
        self.ensure_headers(id_)
        # Then we can display the test name/status itself.
        self.display_result(id_)

    def split(self, id_):
        # Split on pytest's :: joiner, and strip out our intermediate
        # SpecInstance objects (appear as '()')
        headers = [x for x in id_.split('::')[1:] if x != '()']
        # Last one is the actual test being reported on, not a header
        leaf = headers.pop()
        return headers, leaf

    def ensure_headers(self, id_):
        headers, _ = self.split(id_)
        printed = False
        # TODO: this works for class-based tests but needs love for module ones
        # TODO: worth displaying filename ever?
        # Make sure we print all not-yet-seen headers
        for i, header in enumerate(headers):
            # Need to semi-uniq headers by their 'path'. (This is a lot like
            # "the test id minus the last segment" but since we have to
            # split/join either way...whatever. I like dots.)
            header_path = '.'.join(headers[:i + 1])
            if header_path in self.headers_displayed:
                continue
            self.headers_displayed.append(header_path)
            indent = self.indent * i
            # TODO: is raw print() correct here? What's the parent class do?
            print("\n{}{}".format(indent, header))
            printed = True
        # No trailing blank line after all headers; only the 'last' one (i.e.
        # before any actual test names are printed). And only if at least one
        # header was actually printed! (Otherwise one gets newlines between all
        # tests.)
        if printed:
            print("")

    def display_result(self, id_):
        # TODO: just pass in what is needed from report
        headers, leaf = self.split(id_)
        indent = self.indent * len(headers)
        print("{}{}".format(indent, leaf))
