import inspect
import types
from pathlib import Path

import six

from pytest import __version__ as pytest_version
from pytest import Class, Module

# NOTE: don't see any other way to get access to pytest innards besides using
# the underscored name :(
from _pytest.python import PyCollector

pytest_version_info = tuple(map(int, pytest_version.split(".")[:3]))

# https://docs.pytest.org/en/latest/deprecations.html#the-pytest-instance-collector
# The pytest.Instance collector type has been removed in Pytest 7.0
if pytest_version_info < (7, 0, 0):
    from pytest import Instance
else:
    Instance = object

# NOTE: these are defined here for reuse by both pytest's own machinery and our
# internal bits.
def istestclass(name):
    return not name.startswith("_")


def istestfunction(name):
    return not (name.startswith("_") or name in ("setup", "teardown"))

def _get_obj_rec(obj, parent_obj):
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
        if isinstance(value, six.class_types):
            continue
        # Methods may get skipped, or not, depending:
        if isinstance(value, types.MethodType):
            # If they look like tests, they get skipped; don't want to copy
            # tests around!
            if istestfunction(name):
                continue
            # Non-test == they're probably lifecycle methods
            # (setup/teardown) or helpers (_do_thing). Rebind them to the
            # target instance, otherwise the 'self' in the setup/helper is
            # not the same 'self' as that in the actual test method it runs
            # around or within!
            # TODO: arguably, all setup or helper methods should become
            # autouse class fixtures (see e.g. pytest docs under 'xunit
            # setup on steroids')
            func = six.get_method_function(value)
            setattr(obj, name, six.create_bound_method(func, obj))
            continue
        # Same as above but for Pytest 7 which does
        # collect methods as functions, and without the six wrapper.
        if isinstance(value, types.FunctionType) and istestfunction(name):
            continue
        # Anything else should be some data-type attribute, which is copied
        # verbatim / by-value.
        setattr(obj, name, value)
    return obj

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

    @classmethod
    def from_parent(cls, parent, fspath):
        if pytest_version_info >= (7, 0):
            return super(SpecModule, cls).from_parent(parent, path=Path(fspath))
        elif pytest_version_info >= (5, 4):
            return super(SpecModule, cls).from_parent(parent, fspath=fspath)
        else:
            return cls(parent=parent, fspath=fspath)

    def _is_test_obj(self, test_func, obj, name):
        # First run our super() test, which should be RelaxedMixin's.
        good_name = getattr(super(SpecModule, self), test_func)(obj, name)
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
        # Get whatever our parent picked up as valid test items (given our
        # relaxed name constraints above). It'll be nearly all module contents.
        items = super(SpecModule, self).collect()

        collected = []
        for item in items:
            # Replace Class objects with recursive SpecInstances (via
            # SpecClasses, so we don't lose some bits of parent Class).
            # TODO: this may be way more than is necessary; possible we can
            # recurse & unpack here, as long as we preserve parent/child
            # relationships correctly?
            # NOTE: we could explicitly skip unittest objects here (we'd want
            # them to be handled by pytest's own unittest support) but since
            # those are almost always in test_prefixed_filenames anyways...meh
            if isinstance(item, Class):
                item = SpecClass.from_parent(item.parent, name=item.name)
            collected.append(item)
        return collected


class SpecClass(RelaxedMixin, Class):

    @classmethod
    def from_parent(cls, parent, name):
        if pytest_version_info >= (5, 4):
            return super(SpecClass, cls).from_parent(parent, name=name)
        else:
            return cls(parent=parent, name=name)

    def collect(self):
        items = super(SpecClass, self).collect()
        collected = []
        for item in items:
            if pytest_version_info < (7, 0):
                # Replace Instance objects with SpecInstance objects that know how to
                # recurse into inner classes.
                item = SpecInstance.from_parent(item.parent, name=item.name)
                collected.append(item)
            else:
                # Pytest >= 7 collects the Functions in Class directly without Instance
                # Replace any Class objects with SpecClass, and recurse into it.
                if isinstance(item, Class):
                    subclass = SpecClass.from_parent(item.parent, name=item.name)
                    collected += subclass.collect()
                else:
                    collected.append(item)
        return collected

    def _getobj(self):
        # Regular object-making first
        obj = super(SpecClass, self)._getobj()
        # Then decorate it with our parent's extra attributes, allowing nested
        # test classes to appear as an aggregate of parents' "scopes".
        # NOTE: of course, skipping if we've gone out the top into a module etc
        if (
            pytest_version_info < (7, 0)
            or not hasattr(self, "parent")
            or not isinstance(self.parent, SpecClass)
        ):
            return obj
        else:
            return _get_obj_rec(obj, self.parent.obj)

class SpecInstance(RelaxedMixin, Instance):
    # This is only instantiated in Pytest < 7

    @classmethod
    def from_parent(cls, parent, name):
        if pytest_version_info >= (5, 4):
            return super(SpecInstance, cls).from_parent(parent, name=name)
        else:
            return cls(parent=parent, name=name)

    def _getobj(self):
        # Regular object-making first
        obj = super(SpecInstance, self)._getobj()
        # Then decorate it with our parent's extra attributes, allowing nested
        # test classes to appear as an aggregate of parents' "scopes".
        # NOTE: need parent.parent due to instance->class hierarchy
        # NOTE: of course, skipping if we've gone out the top into a module etc
        if (
            not hasattr(self, "parent")
            or not hasattr(self.parent, "parent")
            or not isinstance(self.parent.parent, SpecInstance)
        ):
            return obj
        else:
            return _get_obj_rec(obj, self.parent.parent.obj)


    def collect(self):
        items = super(SpecInstance, self).collect()
        collected = []
        for item in items:
            # Replace any Class objects with SpecClass, and recurse into it.
            if isinstance(item, Class):
                cls = SpecClass.from_parent(item.parent, name=item.name)
                for item in cls.collect():
                    collected.append(item)
            else:
                collected.append(item)
        return collected
