import unittest
import pytest
import azure.cosmos.diagnostics as m

_headers = {
    'x-ms-foo': 'foo',
    'bar': 'bar'
}

class BaseUnitTests(unittest.TestCase):

    def test_init(self):
        rh = m.RecordHeaders()
        assert rh.headers == {}

    def test_headers(self):
        rh = m.RecordHeaders()
        rh(_headers)
        assert rh.headers == _headers
        assert rh.headers is not _headers

    def test_attrs(self):
        rh = m.RecordHeaders()
        rh(_headers)
        assert rh.foo == "foo"
        with pytest.raises(AttributeError):
            rh.bar
