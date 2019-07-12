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
try:
    from unittest import mock
except ImportError:
    import mock

import requests

import pytest

from azure.core import PipelineClient
from azure.core.exceptions import DecodeError
from azure.core.configuration import Configuration
from azure.core.pipeline import (
    PipelineResponse,
    PipelineRequest,
    PipelineContext
)
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
)
from azure.core.pipeline.transport import RequestsTransportResponse

from azure.core.pipeline.policies.universal import (
    NetworkTraceLoggingPolicy,
    ContentDecodePolicy,
    UserAgentPolicy,
    HeadersPolicy,
    TelemetryPolicy
)


def test_telemetry_policy():
    url = "https://bing.com"
    config = Configuration()
    config.headers_policy = HeadersPolicy()
    config.telemetry_policy = TelemetryPolicy("storage/1.01")

    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(
        request,
        user_agent="AzCopy/10.0.4-Preview"
    )
    request = pipeline_response.http_request
    user_agent = request.headers.get('User-Agent')
    assert user_agent.startswith('AzCopy/10.0.4-Preview azsdk-python-storage/1.01')


def test_telemetry_policy_keep_existing_user_agent():
    url = "https://bing.com"
    config = Configuration()
    config.headers_policy = HeadersPolicy({'User-Agent': 'ExistingUserAgentValue'})
    config.telemetry_policy = TelemetryPolicy("storage/1.01")

    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(
        request,
        user_agent="AzCopy/10.0.4-Preview"
    )
    request = pipeline_response.http_request
    user_agent = request.headers.get('User-Agent')
    assert user_agent.startswith('AzCopy/10.0.4-Preview azsdk-python-storage/1.01')
    assert user_agent.find('ExistingUserAgentValue')


def test_telemetry_policy_with_dynamic_telemetry():
    url = "https://bing.com"
    config = Configuration()
    config.headers_policy = HeadersPolicy()
    config.telemetry_policy = TelemetryPolicy("storage/1.01")

    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(
        request,
        user_agent="AzCopy/10.0.4-Preview",
        telemetry="class=BlobClient;method=DownloadFile;blobType=Block"
    )

    request = pipeline_response.http_request
    user_agent = request.headers.get('User-Agent')
    telemetry = request.headers.get('X-MS-AZSDK-Telemetry')
    assert user_agent.startswith('AzCopy/10.0.4-Preview azsdk-python-storage/1.01')
    assert telemetry == 'class=BlobClient;method=DownloadFile;blobType=Block'


def test_telemetry_policy_with_telemetry_disabled():
    with mock.patch.dict('os.environ', {'AZURE_TELEMETRY_DISABLED': "True"}):
        policy = TelemetryPolicy('storage/1.01')

        request = HttpRequest('GET', 'https://bing.com')
        policy.on_request(PipelineRequest(request, PipelineContext(None)))
        assert request.headers.get("user-agent", None) is None


def test_telemetry_policy_with_overwrite():
    url = "https://bing.com"
    config = Configuration()
    config.headers_policy = HeadersPolicy({'User-Agent': 'ExistingUserAgentValue'})
    config.telemetry_policy = TelemetryPolicy("storage/1.01")

    client = PipelineClient(base_url=url, config=config)
    request = client.get(url)
    pipeline_response = client._pipeline.run(
        request,
        user_agent="OverwritingUserAgent",
        user_agent_overwrite=True
    )

    request = pipeline_response.http_request
    user_agent = request.headers.get('User-Agent')
    assert user_agent == 'OverwritingUserAgent'


def test_telemetry_policy_from_environment():
    with mock.patch.dict('os.environ', {'AZURE_HTTP_USER_AGENT': "UserAgentFromEnv"}):
        policy = TelemetryPolicy(user_agent_use_env=True)

        request = HttpRequest('GET', 'https://bing.com')
        policy.on_request(PipelineRequest(request, PipelineContext(None)))
        assert request.headers["user-agent"].endswith("UserAgentFromEnv")


def test_user_agent():

    with mock.patch.dict('os.environ', {'AZURE_HTTP_USER_AGENT': "mytools"}):
        policy = UserAgentPolicy(None)
        assert policy.user_agent.endswith("mytools")

        request = HttpRequest('GET', 'http://127.0.0.1/')
        policy.on_request(PipelineRequest(request, PipelineContext(None)))
        assert request.headers["user-agent"].endswith("mytools")

@mock.patch('azure.core.pipeline.policies.universal._LOGGER')
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


def test_raw_deserializer():
    raw_deserializer = ContentDecodePolicy()

    def build_response(body, content_type=None):
        class MockResponse(HttpResponse):
            def __init__(self, body, content_type):
                super(MockResponse, self).__init__(None, None)
                self._body = body
                self.content_type = None
                if content_type:
                    self.content_type = [content_type]

            def body(self):
                return self._body
        return PipelineResponse(None, MockResponse(body, content_type), PipelineContext(None, stream=False))

    response = build_response(b"<groot/>", content_type="application/xml")
    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result.tag == "groot"

    # The basic deserializer works with unicode XML
    response = build_response(u'<groot language="français"/>'.encode('utf-8'), content_type="application/xml")
    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result.attrib["language"] == u"français"

    # Catch some weird situation where content_type is XML, but content is JSON
    response = build_response(b'{"ugly": true}', content_type="application/xml")
    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result["ugly"] is True

    # Be sure I catch the correct exception if it's neither XML nor JSON
    with pytest.raises(DecodeError):
        response = build_response(b'gibberish', content_type="application/xml")
        raw_deserializer.on_response(None, response,)
    with pytest.raises(DecodeError):
        response = build_response(b'{{gibberish}}', content_type="application/xml")
        raw_deserializer.on_response(None, response)

    # Simple JSON
    response = build_response(b'{"success": true}', content_type="application/json")
    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True

    # For compat, if no content-type, decode JSON
    response = build_response(b'"data"')
    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result == "data"

    # Try with a mock of requests

    req_response = requests.Response()
    req_response.headers["content-type"] = "application/json"
    req_response._content = b'{"success": true}'
    req_response._content_consumed = True
    response = PipelineResponse(None, RequestsTransportResponse(None, req_response), PipelineContext(None, stream=False))

    raw_deserializer.on_response(None, response)
    result = response.context["deserialized_data"]
    assert result["success"] is True
