"""
Test decorator for capturing stdout/stderr/both.

Based on original code from Fabric 1.x, specifically:

* fabric/tests/utils.py
* as of Git SHA 62abc4e17aab0124bf41f9c5f9c4bc86cc7d9412

Though modifications have been made since.
"""

import io
import sys
from functools import wraps


class CarbonCopy(io.BytesIO):
    """
    An IO wrapper capable of multiplexing its writes to other buffer objects.
    """

    def __init__(self, buffer=b"", cc=None):
        """
        If ``cc`` is given and is a file-like object or an iterable of same,
        it/they will be written to whenever this instance is written to.
        """
        super().__init__(buffer)
        if cc is None:
            cc = []
        elif hasattr(cc, "write"):
            cc = [cc]
        self.cc = cc

    def write(self, s):
        # Ensure we always write bytes. This means that wrapped code calling
        # print(<a string object>) in Python 3 will still work. Sigh.
        if isinstance(s, str):
            s = s.encode("utf-8")
        # Write out to our capturing object & any CC's
        super().write(s)
        for writer in self.cc:
            writer.write(s)

    # Real sys.std(out|err) (as of Python 3) requires writing to a buffer
    # attribute obj in some situations.
    @property
    def buffer(self):
        return self

    # Make sure we always hand back strings, even on Python 3
    def getvalue(self):
        ret = super().getvalue()
        if isinstance(ret, bytes):
            ret = ret.decode("utf-8")
        return ret


def trap(func):
    """
    Replace sys.std(out|err) with a wrapper during execution, restored after.

    In addition, a new combined-streams output (another wrapper) will appear at
    ``sys.stdall``. This stream will resemble what a user sees at a terminal,
    i.e. both out/err streams intermingled.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Use another CarbonCopy even though we're not cc'ing; for our "write
        # bytes, return strings on py3" behavior. Meh.
        sys.stdall = CarbonCopy()
        my_stdout, sys.stdout = sys.stdout, CarbonCopy(cc=sys.stdall)
        my_stderr, sys.stderr = sys.stderr, CarbonCopy(cc=sys.stdall)
        try:
            return func(*args, **kwargs)
        finally:
            sys.stdout = my_stdout
            sys.stderr = my_stderr
            del sys.stdall

    return wrapper
