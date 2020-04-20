# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the retry policy."""
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
import sys
import mock
import pytest
from azure.core.exceptions import AzureError, ServiceResponseError, ServiceResponseTimeoutError
from azure.core.pipeline.policies import (
    AsyncRetryPolicy,
    RetryMode,
)
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.transport import (
    HttpRequest,
    HttpResponse,
    AsyncHttpTransport,
)
import tempfile
import os
import time
import asyncio

def test_retry_code_class_variables():
    retry_policy = AsyncRetryPolicy()
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
    retry_policy = AsyncRetryPolicy()
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

    retry_policy = AsyncRetryPolicy(retry_mode=RetryMode.Fixed)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 1

    retry_policy = AsyncRetryPolicy(retry_mode=RetryMode.Exponential)
    backoff_time = retry_policy.get_backoff_time(settings)
    assert backoff_time == 4

@pytest.mark.parametrize("retry_after_input", [('0'), ('800'), ('1000'), ('1200')])
def test_retry_after(retry_after_input):
    retry_policy = AsyncRetryPolicy()
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
    retry_policy = AsyncRetryPolicy()
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

@pytest.mark.asyncio
async def test_retry_on_429():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._count = 0
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = HttpResponse(request, None)
            response.status_code = 429
            return response

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_retry = AsyncRetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = AsyncPipeline(transport, [http_retry])
    await pipeline.run(http_request)
    assert transport._count == 2

@pytest.mark.asyncio
async def test_no_retry_on_201():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._count = 0
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self._count += 1
            response = HttpResponse(request, None)
            response.status_code = 201
            headers = {"Retry-After": "1"}
            response.headers = headers
            return response

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    http_retry = AsyncRetryPolicy(retry_total = 1)
    transport = MockTransport()
    pipeline = AsyncPipeline(transport, [http_retry])
    await pipeline.run(http_request)
    assert transport._count == 1

@pytest.mark.asyncio
async def test_retry_seekable_stream():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
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
    http_retry = AsyncRetryPolicy(retry_total = 1)
    pipeline = AsyncPipeline(MockTransport(), [http_retry])
    await pipeline.run(http_request)

@pytest.mark.asyncio
async def test_retry_seekable_file():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._first = True
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
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
        http_retry = AsyncRetryPolicy(retry_total=1)
        pipeline = AsyncPipeline(MockTransport(), [http_retry])
        await pipeline.run(http_request)
    os.unlink(f.name)

@pytest.mark.asyncio
async def test_retry_timeout():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self.count = 0

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):  # type: (PipelineRequest, Any) -> PipelineResponse
            self.count += 1
            if self.count > 2:
                assert self.count <= 2
            time.sleep(0.5)
            raise ServiceResponseError('timeout')

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    headers = {'Content-Type': "multipart/form-data"}
    http_request.headers = headers
    http_retry = AsyncRetryPolicy(retry_total=10, timeout=1)
    pipeline = AsyncPipeline(MockTransport(), [http_retry])
    with pytest.raises(ServiceResponseTimeoutError):
        await pipeline.run(http_request)

