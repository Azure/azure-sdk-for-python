# The MIT License (MIT)
# Copyright (c) 2019 Microsoft Corporation
import unittest

import azure.cosmos.diagnostics as m

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
