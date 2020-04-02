# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
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
#--------------------------------------------------------------------------
import logging
try:
    from unittest import mock
except ImportError:
    import mock

import requests
import pytest

from azure.core.exceptions import DecodeError, AzureError
from azure.core.pipeline import (
    Pipeline,
    PipelineResponse,
    PipelineRequest,
    PipelineContext
)
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
    RequestsTransportResponse,
)

from azure.core.pipeline.policies import (
    NetworkTraceLoggingPolicy,
    ContentDecodePolicy,
    UserAgentPolicy,
    HttpLoggingPolicy,
    RequestHistory,
    RetryPolicy,
    HTTPPolicy,
)

def test_request_history():
    class Non_deep_copiable(object):
        def __deepcopy__(self, memodict={}):
            raise ValueError()

    body = Non_deep_copiable()
    request = HttpRequest('GET', 'http://127.0.0.1/', {'user-agent': 'test_request_history'})
    request.body = body
    request_history = RequestHistory(request)
    assert request_history.http_request.headers == request.headers
    assert request_history.http_request.url == request.url
    assert request_history.http_request.method == request.method

def test_request_history_type_error():
    class Non_deep_copiable(object):
        def __deepcopy__(self, memodict={}):
            raise TypeError()

    body = Non_deep_copiable()
    request = HttpRequest('GET', 'http://127.0.0.1/', {'user-agent': 'test_request_history'})
    request.body = body
    request_history = RequestHistory(request)
    assert request_history.http_request.headers == request.headers
    assert request_history.http_request.url == request.url
    assert request_history.http_request.method == request.method

@mock.patch('azure.core.pipeline.policies._universal._LOGGER')
def test_no_log(mock_http_logger):
    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    request = PipelineRequest(universal_request, PipelineContext(None))
    http_logger = NetworkTraceLoggingPolicy()
    response = PipelineResponse(request, HttpResponse(universal_request, None), request.context)

    # By default, no log handler for HTTP
    http_logger.on_request(request)
    mock_http_logger.debug.assert_not_called()
    http_logger.on_response(request, response)
    mock_http_logger.debug.assert_not_called()
    mock_http_logger.reset_mock()

    # I can enable it per request
    request.context.options['logging_enable'] = True
    http_logger.on_request(request)
    assert mock_http_logger.debug.call_count >= 1
    mock_http_logger.reset_mock()
    request.context.options['logging_enable'] = True
    http_logger.on_response(request, response)
    assert mock_http_logger.debug.call_count >= 1
    mock_http_logger.reset_mock()

    # I can enable it per request (bool value should be honored)
    request.context.options['logging_enable'] = False
    http_logger.on_request(request)
    mock_http_logger.debug.assert_not_called()
    request.context.options['logging_enable'] = False
    http_logger.on_response(request, response)
    mock_http_logger.debug.assert_not_called()
    mock_http_logger.reset_mock()

    # I can enable it globally
    request.context.options = {}
    http_logger.enable_http_logger = True
    http_logger.on_request(request)
    assert mock_http_logger.debug.call_count >= 1
    http_logger.on_response(request, response)
    assert mock_http_logger.debug.call_count >= 1
    mock_http_logger.reset_mock()

    # I can enable it globally and override it locally
    http_logger.enable_http_logger = True
    request.context.options['logging_enable'] = False
    http_logger.on_request(request)
    mock_http_logger.debug.assert_not_called()
    response.context['logging_enable'] = False
    http_logger.on_response(request, response)
    mock_http_logger.debug.assert_not_called()
    mock_http_logger.reset_mock()

    # Let's make this request a failure, retried twice
    request.context.options['logging_enable'] = True
    http_logger.on_request(request)
    http_logger.on_response(request, response)

    first_count = mock_http_logger.debug.call_count
    assert first_count >= 1

    http_logger.on_request(request)
    http_logger.on_response(request, response)

    second_count = mock_http_logger.debug.call_count
    assert second_count == first_count * 2

def test_retry_without_http_response():
    class NaughtyPolicy(HTTPPolicy):
        def send(*args):
            raise AzureError('boo')

    policies = [RetryPolicy(), NaughtyPolicy()]
    pipeline = Pipeline(policies=policies, transport=None)
    with pytest.raises(AzureError):
        pipeline.run(HttpRequest('GET', url='https://foo.bar'))

def test_raw_deserializer():
    raw_deserializer = ContentDecodePolicy()
    context = PipelineContext(None, stream=False)
    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    request = PipelineRequest(universal_request, context)

    def build_response(body, content_type=None):
        class MockResponse(HttpResponse):
            def __init__(self, body, content_type):
                super(MockResponse, self).__init__(None, None)
                self._body = body
                self.content_type = content_type

            def body(self):
                return self._body

        return PipelineResponse(request, MockResponse(body, content_type), context)

    response = build_response(b"<groot/>", content_type="application/xml")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result.tag == "groot"

    response = build_response(b"\xef\xbb\xbf<utf8groot/>", content_type="application/xml")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result.tag == "utf8groot"

    # The basic deserializer works with unicode XML
    response = build_response(u'<groot language="français"/>'.encode('utf-8'), content_type="application/xml")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result.attrib["language"] == u"français"

    # Catch some weird situation where content_type is XML, but content is JSON
    response = build_response(b'{"ugly": true}', content_type="application/xml")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["ugly"] is True

    # Be sure I catch the correct exception if it's neither XML nor JSON
    response = build_response(b'gibberish', content_type="application/xml")
    with pytest.raises(DecodeError) as err:
        raw_deserializer.on_response(request, response)
    assert err.value.response is response.http_response

    response = build_response(b'{{gibberish}}', content_type="application/xml")
    with pytest.raises(DecodeError) as err:
        raw_deserializer.on_response(request, response)
    assert err.value.response is response.http_response

    # Simple JSON
    response = build_response(b'{"success": true}', content_type="application/json")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # Simple JSON with BOM
    response = build_response(b'\xef\xbb\xbf{"success": true}', content_type="application/json")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # Simple JSON with complex content_type
    response = build_response(b'{"success": true}', content_type="application/vnd.microsoft.appconfig.kv.v1+json")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # Simple JSON with complex content_type, v2
    response = build_response(b'{"success": true}', content_type="text/vnd.microsoft.appconfig.kv.v1+json")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # For compat, if no content-type, decode JSON
    response = build_response(b'"data"')
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == "data"

    # Let text/plain let through
    response = build_response(b'I am groot', content_type="text/plain")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == "I am groot"

    # Let text/plain let through + BOM
    response = build_response(b'\xef\xbb\xbfI am groot', content_type="text/plain")
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == "I am groot"

    # Try with a mock of requests

    req_response = requests.Response()
    req_response.headers["content-type"] = "application/json"
    req_response._content = b'{"success": true}'
    req_response._content_consumed = True
    response = PipelineResponse(None, RequestsTransportResponse(None, req_response), PipelineContext(None, stream=False))

    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # I can enable it per request
    request.context.options['response_encoding'] = 'utf-8'
    response = build_response(b'\xc3\xa9', content_type="text/plain")
    raw_deserializer.on_request(request)
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == u"é"
    assert response.context["response_encoding"] == "utf-8"
    del request.context['response_encoding']

    # I can enable it globally
    raw_deserializer = ContentDecodePolicy(response_encoding="utf-8")
    response = build_response(b'\xc3\xa9', content_type="text/plain")
    raw_deserializer.on_request(request)
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == u"é"
    assert response.context["response_encoding"] == "utf-8"
    del request.context['response_encoding']

    # Per request is more important
    request.context.options['response_encoding'] = 'utf-8-sig'
    response = build_response(b'\xc3\xa9', content_type="text/plain")
    raw_deserializer.on_request(request)
    raw_deserializer.on_response(request, response)
    result = response.context["deserialized_data"]
    assert result == u"é"
    assert response.context["response_encoding"] == "utf-8-sig"
    del request.context['response_encoding']

def test_http_logger():

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy(logger=logger)

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 5
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'

    mock_handler.reset()

    # Let's make this request a failure, retried twice

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 10
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'

    mock_handler.reset()

    # Headers and query parameters

    policy.allowed_query_params = ['country']

    universal_request.headers = {
        "Accept": "Caramel",
        "Hate": "Chocolat",
    }
    http_response.headers = {
        "Content-Type": "Caramel",
        "HateToo": "Chocolat",
    }
    universal_request.url = "http://127.0.0.1/?country=france&city=aix"

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 9
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/?country=france&city=REDACTED'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == "Request headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        mock_handler.messages[3].message,
        mock_handler.messages[4].message
    ]) == set([
        "    'Accept': 'Caramel'",
        "    'Hate': 'REDACTED'"
    ])
    assert mock_handler.messages[5].message == "Response status: 202"
    assert mock_handler.messages[6].message == "Response headers:"
    # Dict not ordered in Python, exact logging order doesn't matter
    assert set([
        mock_handler.messages[7].message,
        mock_handler.messages[8].message
    ]) == set([
        "    'Content-Type': 'Caramel'",
        "    'HateToo': 'REDACTED'"
    ])

    mock_handler.reset()

def test_http_logger_operation_level():

    class MockHandler(logging.Handler):
        def __init__(self):
            super(MockHandler, self).__init__()
            self.messages = []
        def reset(self):
            self.messages = []
        def emit(self, record):
            self.messages.append(record)
    mock_handler = MockHandler()

    logger = logging.getLogger("testlogger")
    logger.addHandler(mock_handler)
    logger.setLevel(logging.DEBUG)

    policy = HttpLoggingPolicy()
    kwargs={'logger': logger}

    universal_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_response = HttpResponse(universal_request, None)
    http_response.status_code = 202
    request = PipelineRequest(universal_request, PipelineContext(None, **kwargs))

    # Basics

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 5
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'

    mock_handler.reset()

    # Let's make this request a failure, retried twice

    request = PipelineRequest(universal_request, PipelineContext(None, **kwargs))

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    policy.on_request(request)
    response = PipelineResponse(request, http_response, request.context)
    policy.on_response(request, response)

    assert all(m.levelname == 'INFO' for m in mock_handler.messages)
    assert len(mock_handler.messages) == 10
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'
    assert mock_handler.messages[0].message == "Request URL: 'http://127.0.0.1/'"
    assert mock_handler.messages[1].message == "Request method: 'GET'"
    assert mock_handler.messages[2].message == 'Request headers:'
    assert mock_handler.messages[3].message == 'Response status: 202'
    assert mock_handler.messages[4].message == 'Response headers:'

    mock_handler.reset()
