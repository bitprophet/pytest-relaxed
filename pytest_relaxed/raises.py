from decorator import decorator


# Thought pytest.raises was like nose.raises, but nooooooo. So let's make it
# like that.
def raises(exception):
    @decorator
    def inner(f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exception:
            pass
        else:
            raise Exception("Did not receive expected {}!".format(exception))
    return inner
