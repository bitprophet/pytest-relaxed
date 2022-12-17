import inspect
import logging
import types

from pytest import Class, Module

# NOTE: don't see any other way to get access to pytest innards besides using
# the underscored name :(
from _pytest.python import PyCollector


log = logging.getLogger("relaxed")


# NOTE: these are defined here for reuse by both pytest's own machinery and our
# internal bits.
def istestclass(name):
    return not name.startswith("_")


def istestfunction(name):
    return not (name.startswith("_") or name in ("setup", "teardown"))


# All other classes in here currently inherit from PyCollector, and it is what
# defines the default istestfunction/istestclass, so makes sense to inherit
# from it for our mixin. (PyobjMixin, another commonly found class, offers
# nothing of interest to us however.)
class RelaxedMixin(PyCollector):
    """
    A mixin applying collection rules to both modules and inner/nested classes.
    """

    # TODO:
    # - worth calling super() in these? Difficult to know what to do with it;
    # it would say "no" to lots of stuff we want to say "yes" to.
    # - are there other tests to apply to 'obj' in a vacuum? so far only thing
    # we test 'obj' for is its membership in a module, which must happen inside
    # SpecModule's override.

    def istestclass(self, obj, name):
        return istestclass(name)

    def istestfunction(self, obj, name):
        return istestfunction(name)


class SpecModule(RelaxedMixin, Module):

    def _is_test_obj(self, test_func, obj, name):
        # First run our super() test, which should be RelaxedMixin's.
        good_name = getattr(super(), test_func)(obj, name)
        # If RelaxedMixin said no, we can't really say yes, as the name itself
        # was bad - private, other non test name like setup(), etc
        if not good_name:
            return False
        # Here, we dig further based on our own wrapped module obj, by
        # rejecting anything not defined locally.
        if inspect.getmodule(obj) is not self.obj:
            return False
        # No other complaints -> it's probably good
        return True

    def istestfunction(self, obj, name):
        return self._is_test_obj("istestfunction", obj, name)

    def istestclass(self, obj, name):
        return self._is_test_obj("istestclass", obj, name)

    def collect(self):
        # Given we've overridden naming constraints etc above, just use
        # superclass' collection logic for the rest of the necessary behavior.
        items = super().collect()
        collected = []
        for item in items:
            # Replace Class objects with recursive SpecClasses
            # NOTE: we could explicitly skip unittest objects here (we'd want
            # them to be handled by pytest's own unittest support) but since
            # those are almost always in test_prefixed_filenames anyways...meh
            if isinstance(item, Class):
                item = SpecClass.from_parent(item.parent, name=item.name)
            collected.append(item)
        return collected


class SpecClass(RelaxedMixin, Class):

    def _getobj(self):
        # Regular object-making first
        obj = super()._getobj()
        # Short circuit if this obj isn't a nested class (aka child):
        # - no parent attr: implies module-level obj definition
        # - parent attr, but isn't a class: implies method
        if (
            not hasattr(self, "parent")
            or not isinstance(self.parent, SpecClass)
        ):
            return obj
        # Then decorate it with our parent's extra attributes, allowing nested
        # test classes to appear as an aggregate of parents' "scopes".
        parent_obj = self.parent.obj
        # Obtain parent attributes, etc not found on our obj (serves as both a
        # useful identifier of "stuff added to an outer class" and a way of
        # ensuring that we can override such attrs), and set them on obj
        delta = set(dir(parent_obj)).difference(set(dir(obj)))
        for name in delta:
            value = getattr(parent_obj, name)
            # Pytest's pytestmark attributes always get skipped, we don't want
            # to spread that around where it's not wanted. (Besides, it can
            # cause a lot of collection level warnings.)
            if name == "pytestmark":
                continue
            # Classes get skipped; they'd always just be other 'inner' classes
            # that we don't want to copy elsewhere.
            if isinstance(value, type):
                continue
            # Functions (methods) may get skipped, or not, depending:
            # NOTE: as of pytest 7, for some reason the value appears as a
            # function and not a method (???) so covering both bases...
            if isinstance(value, (types.MethodType, types.FunctionType)):
                # If they look like tests, they get skipped; don't want to copy
                # tests around!
                if istestfunction(name):
                    continue
                # Non-test == they're probably lifecycle methods
                # (setup/teardown) or helpers (_do_thing). Rebind them to the
                # target instance, otherwise the 'self' in the setup/helper is
                # not the same 'self' as that in the actual test method it runs
                # around or within!
                setattr(obj, name, value)
            # Anything else should be some data-type attribute, which is copied
            # verbatim / by-value.
            else:
                setattr(obj, name, value)
        return obj

    def collect(self):
        ret = []
        for item in super().collect():
            # More pytestmark skipping.
            if item.name == "pytestmark":
                continue
            if isinstance(item, Class):
                item = SpecClass.from_parent(parent=item.parent, name=item.name, obj=item.obj)
            ret.append(item)
        return ret
