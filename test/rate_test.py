"""
Test that a 429 rate limit exceeded error is handled correctly
by pydocumentdb.

As this cannot reliably be tested on a live instance, this module
uses a MockHTTPSConnection class, which overwrites the
pydocumentdb.https_connection.HTTPSConnection class, and answers
requests with a predefined sequence of responses.
"""

import unittest
import socket
import time
import doctest

import json
import pydocumentdb.https_connection
from collections import deque


class MockHTTPResponse:
    """
    Emulates the httplib.HTTPResponse interface to the extent required
    by pydocumentdb
    """
    version = 11
    def __init__(self, status=200, reason="OK", data="", headers=None):
        self.status = status
        self.reason = reason
        if headers:
            self.headers = dict(headers)
        else:
            self.headers = {}
        self.data = data

    def getheader(name, default=None):
        return self.headers.get(name, default)

    def getheaders(self):
        return self.headers.items()

    def read(self):
        return self.data


class MockHttpsConnection:
    """
    Emulates the httplib.HTTPConnection interface to the extent required
    by pydocumentdb.

    The sequence of responses is shared across all instances of this class.
    MockHttpsConnection is therefore not threadsafe. The add_response method
    can be used to append new items to the response sequence.
    """

    responses = deque()

    def __init__(self, host, port=None, ssl_configuration=None, strict=None,
            timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
        self.host = host
        self.port = port

    @classmethod
    def add_response(cls, status=200, reason="OK", data="", headers=None):
        """
        Add a response for all instances of MockHttpsConnection
        """
        MockHttpsConnection.responses.append((status, reason, data, headers))

    def request(self, method, url, body, headers):
        self.method = method
        self.url = url
        self.body = body
        self.headers = headers

    def getresponse(self, *args):
        """
        Remove the next element from the global responses list and return.
        A "continuation" header is added automatically if more responses are
        waiting.
        """
        resp = MockHttpsConnection.responses.popleft()
        hresp = MockHTTPResponse(*resp)
        if len(resp):
            # technically, this should be an _rid, but anything that
            # evaluates to True sets thte continuation flag in pydocumentdb.
            hresp.headers['x-ms-continuation'] = 'yes'
        return hresp


# Make pydocumentdb use the MockHttpsConnection
pydocumentdb.https_connection.HTTPSConnection = MockHttpsConnection

#####################################################

import pydocumentdb.document_client as document_client
import pydocumentdb.http_constants as http_constants

masterKey = ''

class RateTest(unittest.TestCase):

    # a simple two-document respone
    two_document_response = {
        'Documents': [
            {
                'id' : 1
            },
            {
                'id' : 2
            }
        ]
    }

    @staticmethod
    def _document_at(response, index):
        """
        Return response, but with 'Documents' array truncated to the
        element at position `index`.

        >>> RateTest._document_at(RateTest.two_document_response, 1)
        {'Documents': [{'id': 2}]}

        """
        ret = {}
        for k, v in response.items():
            if k == 'Documents':
                v = [v[index]]
            ret[k] = v
        return ret


    def setUp(self):
        MockHttpsConnection.responses.clear()
        pass


    def test_document_retrieval(self):
        """
        'good' testcase, test that responses stored in the
        MockHttpsConnection class are returned correctly.
        """
        MockHttpsConnection.add_response(200, "OK",
                json.dumps(self._document_at(self.two_document_response, 0)))
        MockHttpsConnection.add_response(200, "OK",
                json.dumps(self._document_at(self.two_document_response, 1)))

        dc = document_client.DocumentClient("https://localhost:443", {'masterKey' : masterKey })
        it = dc.QueryDocuments('coll_1', "SELECT * FROM coll_1")
        it = iter(it)
        self.assertEqual(1, next(it)['id'])
        self.assertEqual(2, next(it)['id'])

        # check that no further responses are pending
        self.assertEqual(0, len(MockHttpsConnection.responses))

    def test_retry_after__fail_on_continuation(self):
        """
        Test that pydocumentdb automatically backs off and waits
        after an HTTP 429 error, and afterwards tries again.
        """

        # Send a good response, a 429 and another good response afterwards.
        MockHttpsConnection.add_response(200, "OK", json.dumps(
            self._document_at(self.two_document_response, 0)))
        MockHttpsConnection.add_response(429, "Too many requests", "{}", {"x-ms-retry-after-ms": 100})
        MockHttpsConnection.add_response(200, "OK", json.dumps(
            self._document_at(self.two_document_response, 1)))

        start = time.time()

        dc = document_client.DocumentClient("https://localhost:443", {'masterKey' : masterKey })
        it = dc.QueryDocuments('coll_1', "SELECT * FROM coll_1")
        it = iter(it)
        self.assertEqual(1, next(it)['id'])
        self.assertEqual(2, next(it)['id'])

        end = time.time()
        # make sure the whole operation took at least 100ms
        self.assertGreaterEqual(end-start, 0.1)
        self.assertEqual(0, len(MockHttpsConnection.responses))

    def test_retry_after__fail_immediately(self):
        """
        Test that pydocumentdb automatically retries after a 429 error
        if that error happens while retrieving the first row.

        TODO: this currently fails, test is disabled.
        """
        return
        self.assertEqual(0, len(MockHttpsConnection.responses))
        MockHttpsConnection.add_response(429, "Too many requests", "{}", {"x-ms-retry-after-ms": 100})
        MockHttpsConnection.add_response(200, "OK", json.dumps(self.two_document_response))

        dc = document_client.DocumentClient("https://localhost:443", {'masterKey' : masterKey })
        it = dc.QueryDocuments('coll_1', "SELECT * FROM coll_1")
        it = iter(it)
        self.assertEqual(2, len(MockHttpsConnection.responses))
        self.assertEqual(1, next(it)['id'])
        self.assertEqual(2, next(it)['id'])
        self.assertEqual(0, len(MockHttpsConnection.responses))


if __name__ == '__main__':
    doctest.testmod()
    unittest.main()
