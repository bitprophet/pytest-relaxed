from decorator import decorator


# Thought pytest.raises was like nose.raises, but nooooooo. So let's make it
# like that.
def raises(klass):

    @decorator
    def inner(f, *args, **kwargs):
        try:
            f(*args, **kwargs)
        except klass:
            pass
        else:
            raise Exception(
                "Did not receive expected {}!".format(klass.__name__)
            )

    return inner
