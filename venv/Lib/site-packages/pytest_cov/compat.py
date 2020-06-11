try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pytest

StringIO  # pyflakes, this is for re-export


if hasattr(pytest, 'hookimpl'):
    hookwrapper = pytest.hookimpl(hookwrapper=True)
else:
    hookwrapper = pytest.mark.hookwrapper


class SessionWrapper(object):
    def __init__(self, session):
        self._session = session
        if hasattr(session, 'testsfailed'):
            self._attr = 'testsfailed'
        else:
            self._attr = '_testsfailed'

    @property
    def testsfailed(self):
        return getattr(self._session, self._attr)

    @testsfailed.setter
    def testsfailed(self, value):
        setattr(self._session, self._attr, value)


def _attrgetter(attr):
    """
    Return a callable object that fetches attr from its operand.

    Unlike operator.attrgetter, the returned callable supports an extra two
    arg form for a default.
    """
    def fn(obj, *args):
        return getattr(obj, attr, *args)

    return fn


worker = 'slave'  # for compatability with pytest-xdist<=1.22.0
workerid = worker + 'id'
workerinput = _attrgetter(worker + 'input')
workeroutput = _attrgetter(worker + 'output')
