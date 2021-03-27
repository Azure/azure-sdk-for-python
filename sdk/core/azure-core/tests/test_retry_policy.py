# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the retry policy."""
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import pytest
from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import AzureError, ServiceResponseError, ServiceResponseTimeoutError
from azure.core.pipeline.policies import (
    RetryPolicy,
    RetryMode,
)
from azure.core.pipeline import Pipeline, PipelineResponse
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
    HttpTransport,
)
import tempfile
import os
import time

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


def test_retry_code_class_variables():
    retry_policy = RetryPolicy()
    assert retry_policy._RETRY_CODES is not None
    assert 408 in retry_policy._RETRY_CODES
    assert 429 in retry_policy._RETRY_CODES
    assert 501 not in retry_policy._RETRY_CODES

def test_retry_types():
    history = ["1", "2", "3"]
    settings = {
        'history': history,
        'backoff': 1,
        'max_backoff': 10
    }
    retry_policy = RetryPolicy()
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

    retry_policy = RetryPolicy(retry_mode=RetryMode.Fixed)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 1

    retry_policy = RetryPolicy(retry_mode=RetryMode.Exponential)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

@pytest.mark.parametrize("retry_after_input", [('0'), ('800'), ('1000'), ('1200')])
def test_retry_after(retry_after_input):
    retry_policy = RetryPolicy()
    request = HttpRequest("GET", "https://bing.com")
    response = HttpResponse(request, None)
    response.headers["retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds/1000.0
    response.headers.pop("retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)

@pytest.mark.parametrize("retry_after_input", [('0'), ('800'), ('1000'), ('1200')])
def test_x_ms_retry_after(retry_after_input):
    retry_policy = RetryPolicy()
    request = HttpRequest("GET", "https://bing.com")
    response = HttpResponse(request, None)
    response.headers["x-ms-retry-after-ms"] = retry_after_input
    pipeline_response = PipelineResponse(request, response, None)
    retry_after = retry_policy.get_retry_after(pipeline_response)
    seconds = float(retry_after_input)
    assert retry_after == seconds/1000.0
    response.headers.pop("x-ms-retry-after-ms")
    response.headers["Retry-After"] = retry_after_input
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)
    response.headers["x-ms-retry-after-ms"] = 500
    retry_after = retry_policy.get_retry_after(pipeline_response)
    assert retry_after == float(retry_after_input)

def test_retry_on_429():
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = HttpResponse(request, None)
            response.status_code = 429
            return response

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_retry = RetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 2

def test_no_retry_on_201():
    class MockTransport(HttpTransport):
        def __init__(self):
            self._count = 0
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = HttpResponse(request, None)
            response.status_code = 201
            headers = {"Retry-After": "1"}
            response.headers = headers
            return response

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_retry = RetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = Pipeline(transport, [http_retry])
    pipeline.run(http_request)
    assert transport._count == 1

def test_retry_seekable_stream():
    class MockTransport(HttpTransport):
        def __init__(self):
            self._first = True
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                request.body.seek(0,2)
                raise AzureError('fail on first')
            position = request.body.tell()
            assert position == 0
            response = HttpResponse(request, None)
            response.status_code = 400
            return response

    data = BytesIO(b"Lots of dataaaa")
    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_request.set_streamed_data_body(data)
    http_retry = RetryPolicy(retry_total = 1)
    pipeline = Pipeline(MockTransport(), [http_retry])
    pipeline.run(http_request)

def test_retry_seekable_file():
    class MockTransport(HttpTransport):
        def __init__(self):
            self._first = True
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def close(self):
            pass
        def open(self):
            pass

        def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            if self._first:
                self._first = False
                for value in request.files.values():
                    name, body = value[0], value[1]
                    if name and body and hasattr(body, 'read'):
                        body.seek(0,2)
                        raise AzureError('fail on first')
            for value in request.files.values():
                name, body = value[0], value[1]
                if name and body and hasattr(body, 'read'):
                    position = body.tell()
                    assert not position
                    response = HttpResponse(request, None)
                    response.status_code = 400
                    return response

    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(b'Lots of dataaaa')
    file.close()
    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    headers = {'Content-Type': "multipart/form-data"}
    http_request.headers = headers
    with open(file.name, 'rb') as f:
        form_data_content = {
            'fileContent': f,
            'fileName': f.name,
        }
        http_request.set_formdata_body(form_data_content)
        http_retry = RetryPolicy(retry_total=1)
        pipeline = Pipeline(MockTransport(), [http_retry])
        pipeline.run(http_request)
    os.unlink(f.name)


def test_retry_timeout():
    timeout = 1

    def send(request, **kwargs):
        assert kwargs["connection_timeout"] <= timeout, "policy should set connection_timeout not to exceed timeout"
        raise ServiceResponseError("oops")

    transport = Mock(
        spec=HttpTransport,
        send=Mock(wraps=send),
        connection_config=ConnectionConfiguration(connection_timeout=timeout * 2),
        sleep=time.sleep,
    )
    pipeline = Pipeline(transport, [RetryPolicy(timeout=timeout)])

    with pytest.raises(ServiceResponseTimeoutError):
        response = pipeline.run(HttpRequest("GET", "http://127.0.0.1/"))


def test_timeout_defaults():
    """When "timeout" is not set, the policy should not override the transport's timeout configuration"""

    def send(request, **kwargs):
        for arg in ("connection_timeout", "read_timeout"):
            assert arg not in kwargs, "policy should defer to transport configuration when not given a timeout"
        response = HttpResponse(request, None)
        response.status_code = 200
        return response

    transport = Mock(
        spec_set=HttpTransport,
        send=Mock(wraps=send),
        sleep=Mock(side_effect=Exception("policy should not sleep: its first send succeeded")),
    )
    pipeline = Pipeline(transport, [RetryPolicy()])

    pipeline.run(HttpRequest("GET", "http://127.0.0.1/"))
    assert transport.send.call_count == 1, "policy should not retry: its first send succeeded"
