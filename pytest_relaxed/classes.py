import inspect
import types

import six

from pytest import Class, Instance, Module
# NOTE: don't see any other way to get access to pytest innards besides using
# the underscored name :(
from _pytest.python import PyCollector


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
        return not name.startswith('_')

    def istestfunction(self, obj, name):
        return not (
            name.startswith('_')
            or name in ('setup', 'teardown')
        )


class SpecModule(RelaxedMixin, Module):
    def istestfunction(self, obj, name):
        # First run our super() test, which should be RelaxedMixin's.
        good_name = super(SpecModule, self).istestfunction(obj, name)
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
            if isinstance(item, Class):
                item = SpecClass(item.name, item.parent)
            # Collect regardless of whether we replaced the item
            collected.append(item)
        return collected


# NOTE: no need to inherit from RelaxedMixin here as it doesn't do much by
# its lonesome
class SpecClass(Class):
    def collect(self):
        items = super(SpecClass, self).collect()
        collected = []
        # Replace Instance objects with SpecInstance objects that know how to
        # recurse into inner classes.
        # TODO: is this ever not a one-item list? Meh.
        for item in items:
            item = SpecInstance(name=item.name, parent=item.parent)
            collected.append(item)
        return collected


class SpecInstance(RelaxedMixin, Instance):
    def _getobj(self):
        # Regular object-making first
        obj = super(SpecInstance, self)._getobj()
        # Then decorate it with our parent's extra attributes, allowing nested
        # test classes to appear as an aggregate of parents' "scopes".
        # NOTE: need parent.parent due to instance->class hierarchy
        # NOTE: of course, skipping if we've gone out the top into a module etc
        if (
            not hasattr(self, 'parent')
            or not hasattr(self.parent, 'parent')
            or not isinstance(self.parent.parent, SpecInstance)
        ):
            return obj
        parent_obj = self.parent.parent.obj
        # Obtain parent attributes not found on our obj (serves as both a
        # useful identifier of "stuff added to an outer class" and a way of
        # ensuring that we can override such attrs), and set them on obj
        delta = set(dir(parent_obj)).difference(set(dir(obj)))
        for name in delta:
            value = getattr(parent_obj, name)
            # Skip past anything that looks like a method or class
            if (
                isinstance(value, six.class_types)
                or isinstance(value, types.MethodType)
            ):
                continue
            setattr(obj, name, value)
        return obj

    def makeitem(self, name, obj):
        # NOTE: no need to modify collect() this time, just mutate item
        # creation.
        # TODO: can't we redo SpecClass the same way? And SpecModule??
        item = super(SpecInstance, self).makeitem(name, obj)
        # Replace any Class objects with SpecClass; this will automatically
        # recurse.
        # TODO: can we unify this with SpecModule's same bits?
        if isinstance(item, Class):
            item = SpecClass(item.name, item.parent)
        return item
