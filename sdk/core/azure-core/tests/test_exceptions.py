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
from azure.core.exceptions import HttpResponseError, ODataV4Error, ODataV4Format
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.core.pipeline.transport._base import _HttpResponseBase


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


class FakeErrorOne(object):

    def __init__(self):
        self.error = Mock(message="A fake error", code="FakeErrorOne")


class FakeErrorTwo(object):

    def __init__(self):
        self.code = "FakeErrorTwo"
        self.message = "A different fake error"


class FakeHttpResponse(HttpResponseError):

    def __init__(self, response, error, *args, **kwargs):
        self.error = error
        super(FakeHttpResponse, self).__init__(self, response=response, *args, **kwargs)


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

    def test_error_continuation_token(self):
        error = HttpResponseError(message="Specific error message", continuation_token='foo')
        assert str(error) == "Specific error message"
        assert error.message == "Specific error message"
        assert error.response is None
        assert error.reason is None
        assert error.error is None
        assert error.status_code is None
        assert error.continuation_token == 'foo'

    def test_deserialized_httpresponse_error_code(self):
        """This is backward compat support of autorest azure-core (KV 4.0.0, Storage 12.0.0).

        Do NOT adapt this test unless you know what you're doing.
        """
        message = {
            "error": {
                "code": "FakeErrorOne",
                "message": "A fake error",
            }
        }
        response = _build_response(json.dumps(message).encode("utf-8"))
        error = FakeHttpResponse(response, FakeErrorOne())
        assert error.message == "(FakeErrorOne) A fake error"
        assert str(error.error) == "(FakeErrorOne) A fake error"
        assert error.error.code == "FakeErrorOne"
        assert error.error.message == "A fake error"
        assert error.response is response
        assert error.reason == "Bad Request"
        assert error.status_code == 400
        assert isinstance(error.model, FakeErrorOne)
        assert isinstance(error.error, ODataV4Format)

        # Could test if we see a deprecation warning
        assert error.error.error.code == "FakeErrorOne"
        assert error.error.error.message == "A fake error"


    def test_deserialized_httpresponse_error_message(self):
        """This is backward compat support for weird responses, adn even if it's likely
        just the autorest testserver, should be fine parsing.

        Do NOT adapt this test unless you know what you're doing.
        """
        message = {
            "code": "FakeErrorTwo",
            "message": "A different fake error",
        }
        response = _build_response(json.dumps(message).encode("utf-8"))
        error = FakeHttpResponse(response, FakeErrorTwo())
        assert error.message == "(FakeErrorTwo) A different fake error"
        assert str(error.error) == "(FakeErrorTwo) A different fake error"
        assert error.error.code == "FakeErrorTwo"
        assert error.error.message == "A different fake error"
        assert error.response is response
        assert error.reason == "Bad Request"
        assert error.status_code == 400
        assert isinstance(error.model, FakeErrorTwo)
        assert isinstance(error.error, ODataV4Format)

    def test_httpresponse_error_with_response(self):
        response = requests.get("https://bing.com")
        http_response = RequestsTransportResponse(None, response)

        error = HttpResponseError(response=http_response)
        assert error.message == "Operation returned an invalid status 'OK'"
        assert error.response is not None
        assert error.reason == 'OK'
        assert isinstance(error.status_code, int)
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

    def test_broken_odata_details(self):
        """Do not block creating a nice exception if "details" only is broken
        """
        message = {
            "error": {
                "code": "Conflict",
                "message": "The maximum number of Free ServerFarms allowed in a Subscription is 10.",
                "target": None,
                "details": [
                    {
                        "message": "The maximum number of Free ServerFarms allowed in a Subscription is 10."
                    },
                    {"code": "Conflict"},
                    {
                        "errorentity": {
                            "code": "Conflict",
                            "message": "The maximum number of Free ServerFarms allowed in a Subscription is 10.",
                            "extendedCode": "59301",
                            "messageTemplate": "The maximum number of {0} ServerFarms allowed in a Subscription is {1}.",
                            "parameters": ["Free", "10"],
                            "innerErrors": None,
                        }
                    },
                ],
                "innererror": None,
            }
        }
        exp = HttpResponseError(response=_build_response(json.dumps(message).encode("utf-8")))
        assert exp.error.code == "Conflict"
