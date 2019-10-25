# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import json
import logging
import os

import requests
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock

# module under test
from azure.core.exceptions import HttpResponseError, ODataV4Error
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.core.pipeline.transport._base import _HttpResponseBase


class FakeErrorOne(object):

    def __init__(self):
        self.error = Mock(message="A fake error", code="FakeErrorOne")


class FakeErrorTwo(object):

    def __init__(self):
        self.message = "A different fake error"


class FakeHttpResponse(HttpResponseError):

    def __init__(self, error, *args, **kwargs):
        self.error = error
        super(FakeHttpResponse, self).__init__(self, *args, **kwargs)


def _build_response(json_body):
    class MockResponse(_HttpResponseBase):
        def __init__(self):
            super(MockResponse, self).__init__(
                request=None,
                internal_response = None,
            )
            self.status_code = 400
            self.reason = "Bad Request"
            self.content_type = "application/json"
            self._body = json_body

        def body(self):
            return self._body

    return MockResponse()

class TestExceptions(object):

    def test_empty_httpresponse_error(self):
        error = HttpResponseError()
        assert str(error) == "Operation returned an invalid status 'None'"
        assert error.message == "Operation returned an invalid status 'None'"
        assert error.response is None
        assert error.reason is None
        assert error.error is None
        assert error.status_code is None

    def test_message_httpresponse_error(self):
        error = HttpResponseError(message="Specific error message")
        assert str(error) == "Specific error message"
        assert error.message == "Specific error message"
        assert error.response is None
        assert error.reason is None
        assert error.error is None
        assert error.status_code is None

    def test_deserialized_httpresponse_error_code(self):
        error = FakeHttpResponse(FakeErrorOne())
        assert error.message == "(FakeErrorOne) A fake error"
        assert error.response is None
        assert error.reason is None
        assert error.status_code is None
        assert isinstance(error.error, FakeErrorOne)

    def test_deserialized_httpresponse_error_message(self):
        error = FakeHttpResponse(FakeErrorTwo())
        assert error.message == "A different fake error"
        assert error.response is None
        assert error.reason is None
        assert error.status_code is None
        assert isinstance(error.error, FakeErrorTwo)

    def test_httpresponse_error_with_response(self):
        response = requests.get("https://bing.com")
        http_response = RequestsTransportResponse(None, response)

        error = HttpResponseError(response=http_response)
        assert error.message == "Operation returned an invalid status 'OK'"
        assert error.response is not None
        assert error.reason == 'OK'
        assert error.status_code == 200
        assert error.error is None

    def test_odata_v4_exception(self):
        message = {
            "error": {
                "code": "501",
                "message": "Unsupported functionality",
                "target": "query",
                "details": [{
                    "code": "301",
                    "target": "$search",
                    "message": "$search query option not supported",
                }],
                "innererror": {
                    "trace": [],
                    "context": {}
                }
            }
        }
        exp = ODataV4Error(_build_response(json.dumps(message).encode("utf-8")))

        assert exp.code == "501"
        assert exp.message == "Unsupported functionality"
        assert exp.target == "query"
        assert exp.details[0].code == "301"
        assert exp.details[0].target == "$search"
        assert "trace" in exp.innererror
        assert "context" in exp.innererror

        message = {}
        exp = ODataV4Error(_build_response(json.dumps(message).encode("utf-8")))
        assert exp.message == "Operation returned an invalid status 'Bad Request'"

        exp = ODataV4Error(_build_response(b""))
        assert exp.message == "Operation returned an invalid status 'Bad Request'"
        assert str(exp) == "Operation returned an invalid status 'Bad Request'"

    def test_odata_v4_minimal(self):
        """Minimal valid OData v4 is code/message and nothing else.
        """
        message = {
            "error": {
                "code": "501",
                "message": "Unsupported functionality",
            }
        }
        exp = ODataV4Error(_build_response(json.dumps(message).encode("utf-8")))
        assert exp.code == "501"
        assert exp.message == "Unsupported functionality"
        assert exp.target is None
        assert exp.details == []
        assert exp.innererror == {}
