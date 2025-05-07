# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

import azure.cosmos.diagnostics as m

_common = {
    'x-ms-activity-id',
    'x-ms-session-token',
    'x-ms-item-count',
    'x-ms-request-quota',
    'x-ms-resource-usage',
    'x-ms-retry-after-ms',
}

_headers = dict(zip(_common, _common))
_headers['other'] = 'other'


@pytest.mark.cosmosEmulator
class TestOldDiagnostics(unittest.TestCase):

    def test_init(self):
        rh = m.RecordDiagnostics()
        assert rh.headers == {}

    def test_headers(self):
        rh = m.RecordDiagnostics()
        rh(_headers, "body")
        assert rh.headers == _headers
        assert rh.headers is not _headers

    def test_headers_case(self):
        rh = m.RecordDiagnostics()
        rh(_headers, "body")
        rh_headers = rh.headers
        for key in rh.headers.keys():
            assert key.upper() in rh_headers
            assert key.lower() in rh_headers

    def test_common_attrs(self):
        rh = m.RecordDiagnostics()
        rh(_headers, "body")
        for name in _common:
            assert rh.headers[name] == name
            attr = name.replace('x-ms-', '').replace('-', '_')
            assert getattr(rh, attr) == name

    def test_other_attrs(self):
        rh = m.RecordDiagnostics()
        rh(_headers, "body")
        assert rh.headers['other'] == 'other'
        with self.assertRaises(AttributeError):
            rh.other


if __name__ == '__main__':
    unittest.main()
