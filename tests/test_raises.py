import pytest

from pytest_relaxed import raises


class Boom(Exception):
    pass


class OtherBoom(Exception):
    pass


class Test_raises(object):

    def test_when_given_exception_raised_no_problem(self):

        @raises(Boom)
        def kaboom():
            raise Boom

        kaboom()
        # If we got here, we're good...

    def test_when_given_exception_not_raised_it_raises_Exception(self):
        # TODO: maybe raise a custom exception later? HEH.
        @raises(Boom)
        def kaboom():
            pass

        # Buffalo buffalo
        with pytest.raises(Exception) as exc:
            kaboom()
        assert "Did not receive expected Boom!" in str(exc.value)

    def test_when_some_other_exception_raised_it_is_untouched(self):

        @raises(Boom)
        def kaboom():
            raise OtherBoom("sup")

        # Buffalo buffalo
        with pytest.raises(OtherBoom) as exc:
            kaboom()
        assert "sup" == str(exc.value)
