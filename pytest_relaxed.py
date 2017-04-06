import inspect

from pytest import Class, Instance, Module


def pytest_collect_file(path, parent):
    # Modify file selection to choose anything not private and not a conftest
    if (
        path.ext == '.py' and
        not path.basename.startswith('_') and
        path.basename != 'conftest.py'
    ):
        # Then use our custom module class which performs modified
        # function/class selection as well as class recursion
        return SpecModule(path, parent)


class RelaxedMixin(object):
    """
    A mixin applying collection rules to both modules and inner/nested classes.
    """
    def classnamefilter(self, name):
        # Override default class detection to accept anything public.
        return not name.startswith('_')

    def funcnamefilter(self, name):
        # Override default func/method detection to accept anything public.
        # TODO: strip out setup/teardown/other special names
        return not name.startswith('_')


class SpecModule(RelaxedMixin, Module):
    def collect(self):
        # Get whatever our parent picked up as valid test items (given our
        # relaxed name constraints above). It'll be nearly all module contents.
        items = super(SpecModule, self).collect()
        collected = []
        for item in items:
            # Filter for only those matches that appear locally defined.
            # TODO: is it better to do this via overriding of
            # istestclass()/istestfunction()?
            # TODO: and if so, can we just fold the name filtering into those
            # too?
            if item.module is not inspect.getmodule(item.obj):
                continue
            # Replace Class objects with recursive SpecInstances (via
            # SpecClasses, so we don't lose some bits of parent Class).
            # TODO: this may be way more than is necessary; possible we can
            # recurse & unpack here, as long as we preserve parent/child
            # relationships correctly?
            if isinstance(item, Class):
                item = SpecClass(item.name, item.parent)
            # Collect
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
