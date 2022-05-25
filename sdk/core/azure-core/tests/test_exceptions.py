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
import pytest
import json
import requests
try:
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    from mock import Mock

# module under test
from azure.core.exceptions import HttpResponseError, ODataV4Error, ODataV4Format, SerializationError, DeserializationError
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.core.pipeline.transport._base import _HttpResponseBase as PipelineTransportHttpResponseBase
from azure.core.rest._http_response_impl import _HttpResponseBaseImpl as RestHttpResponseBase
from utils import HTTP_REQUESTS

class PipelineTransportMockResponse(PipelineTransportHttpResponseBase):
    def __init__(self, json_body):
        super(PipelineTransportMockResponse, self).__init__(
            request=None,
            internal_response = None,
        )
        self.status_code = 400
        self.reason = "Bad Request"
        self.content_type = "application/json"
        self._body = json_body

    def body(self):
        return self._body

class RestMockResponse(RestHttpResponseBase):
    def __init__(self, json_body):
        super(RestMockResponse, self).__init__(
            request=None,
            internal_response=None,
            status_code=400,
            reason="Bad Request",
            content_type="application/json",
            headers={},
            stream_download_generator=None,
        )
        self._body = json_body

    def body(self):
        return self._body

    @property
    def content(self):
        return self._body

MOCK_RESPONSES = [PipelineTransportMockResponse, RestMockResponse]

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

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_deserialized_httpresponse_error_code(self, mock_response):
        """This is backward compat support of autorest azure-core (KV 4.0.0, Storage 12.0.0).

        Do NOT adapt this test unless you know what you're doing.
        """
        message = {
            "error": {
                "code": "FakeErrorOne",
                "message": "A fake error",
            }
        }
        response = mock_response(json.dumps(message).encode("utf-8"))
        error = FakeHttpResponse(response, FakeErrorOne())
        assert "(FakeErrorOne) A fake error" in error.message
        assert "(FakeErrorOne) A fake error" in str(error.error)
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

        assert str(error) == "(FakeErrorOne) A fake error\nCode: FakeErrorOne\nMessage: A fake error"


    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_deserialized_httpresponse_error_message(self, mock_response):
        """This is backward compat support for weird responses, adn even if it's likely
        just the autorest testserver, should be fine parsing.

        Do NOT adapt this test unless you know what you're doing.
        """
        message = {
            "code": "FakeErrorTwo",
            "message": "A different fake error",
        }
        response = mock_response(json.dumps(message).encode("utf-8"))
        error = FakeHttpResponse(response, FakeErrorTwo())
        assert "(FakeErrorTwo) A different fake error" in error.message
        assert "(FakeErrorTwo) A different fake error" in str(error.error)
        assert error.error.code == "FakeErrorTwo"
        assert error.error.message == "A different fake error"
        assert error.response is response
        assert error.reason == "Bad Request"
        assert error.status_code == 400
        assert isinstance(error.model, FakeErrorTwo)
        assert isinstance(error.error, ODataV4Format)

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_httpresponse_error_with_response(self, port, mock_response):
        response = requests.get("http://localhost:{}/basic/string".format(port))
        http_response = RequestsTransportResponse(None, response)

        error = HttpResponseError(response=http_response)
        assert error.message == "Operation returned an invalid status 'OK'"
        assert error.response is not None
        assert error.reason == 'OK'
        assert isinstance(error.status_code, int)
        assert error.error is None

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_odata_v4_exception(self, mock_response):
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
        exp = ODataV4Error(mock_response(json.dumps(message).encode("utf-8")))

        assert exp.code == "501"
        assert exp.message == "Unsupported functionality"
        assert exp.target == "query"
        assert exp.details[0].code == "301"
        assert exp.details[0].target == "$search"
        assert "trace" in exp.innererror
        assert "context" in exp.innererror

        message = {}
        exp = ODataV4Error(mock_response(json.dumps(message).encode("utf-8")))
        assert exp.message == "Operation returned an invalid status 'Bad Request'"

        exp = ODataV4Error(mock_response(b""))
        assert exp.message == "Operation returned an invalid status 'Bad Request'"
        assert str(exp) == "Operation returned an invalid status 'Bad Request'"

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_odata_v4_minimal(self, mock_response):
        """Minimal valid OData v4 is code/message and nothing else.
        """
        message = {
            "error": {
                "code": "501",
                "message": "Unsupported functionality",
            }
        }
        exp = ODataV4Error(mock_response(json.dumps(message).encode("utf-8")))
        assert exp.code == "501"
        assert exp.message == "Unsupported functionality"
        assert exp.target is None
        assert exp.details == []
        assert exp.innererror == {}

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_broken_odata_details(self, mock_response):
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
        exp = HttpResponseError(response=mock_response(json.dumps(message).encode("utf-8")))
        assert exp.error.code == "Conflict"

    @pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
    def test_null_odata_details(self, mock_response):
        message = {
            "error": {
                "code": "501",
                "message": "message",
                "target": None,
                "details": None,
                "innererror": None,
            }
        }
        exp = HttpResponseError(response=mock_response(json.dumps(message).encode("utf-8")))
        assert exp.error.code == "501"

    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    def test_non_odatav4_error_body(self, client, http_request):
        request = http_request("GET", "/errors/non-odatav4-body")
        response = client.send_request(request)
        with pytest.raises(HttpResponseError) as ex:
            response.raise_for_status()
        assert str(ex.value) == "Operation returned an invalid status 'BAD REQUEST'\nContent: {\"code\": 400, \"error\": {\"global\": [\"MY-ERROR-MESSAGE-THAT-IS-COMING-FROM-THE-API\"]}}"

    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    def test_malformed_json(self, client, http_request):
        request = http_request("GET", "/errors/malformed-json")
        response = client.send_request(request)
        with pytest.raises(HttpResponseError) as ex:
            response.raise_for_status()
        assert str(ex.value) == "Operation returned an invalid status 'BAD REQUEST'\nContent: {\"code\": 400, \"error\": {\"global\": [\"MY-ERROR-MESSAGE-THAT-IS-COMING-FROM-THE-API\"]"

    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    def test_text(self, client, http_request):
        request = http_request("GET", "/errors/text")
        response = client.send_request(request)
        with pytest.raises(HttpResponseError) as ex:
            response.raise_for_status()
        assert str(ex.value) == "Operation returned an invalid status 'BAD REQUEST'\nContent: I am throwing an error"

    @pytest.mark.parametrize("http_request", HTTP_REQUESTS)
    def test_datav4_error(self, client, http_request):
        request = http_request("GET", "/errors/odatav4")
        response = client.send_request(request)
        with pytest.raises(HttpResponseError) as ex:
            response.raise_for_status()
        assert "Content: {\"" not in str(ex.value)

def test_serialization_error():
    message = "Oopsy bad input passed for serialization"
    error = SerializationError(message)
    with pytest.raises(SerializationError) as ex:
        raise error
    assert str(ex.value) == message

    with pytest.raises(ValueError) as ex:
        raise error
    assert str(ex.value) == message

def test_deserialization_error():
    message = "Oopsy bad input passed for serialization"
    error = DeserializationError(message)
    with pytest.raises(DeserializationError) as ex:
        raise error
    assert str(ex.value) == message

    with pytest.raises(ValueError) as ex:
        raise error
    assert str(ex.value) == message
