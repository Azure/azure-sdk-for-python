# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import requests
from azure.core.pipeline.transport import (
    HttpRequest as PipelineTransportHttpRequest,
    AsyncHttpResponse as PipelineTransportAsyncHttpResponse,
    AsyncHttpTransport,
    AsyncioRequestsTransportResponse as PipelineTransportAsyncioRequestsTransportResponse,
    AioHttpTransport,
)
from azure.core.pipeline._backcompat import SupportedFormat
from azure.core.pipeline.transport._requests_asyncio import RestAsyncioRequestsTransportResponse
from azure.core.rest import (
    HttpRequest as RestHttpRequest,
    AsyncHttpResponse as RestAsyncHttpResponse,
)
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator
from unittest import mock
import pytest

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type, response_type", [(PipelineTransportHttpRequest, PipelineTransportAsyncHttpResponse), (RestHttpRequest, RestAsyncHttpResponse)])
async def test_connection_error_response(request_type, response_type):
    class MockSession(object):
        def __init__(self):
            self.auto_decompress = True

        @property
        def auto_decompress(self):
            return self.auto_decompress

    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._count = 0
            self.session = MockSession

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        @property
        def supported_formats(self):
            return [SupportedFormat.REST] if hasattr(response_type, "content") else [SupportedFormat.PIPELINE_TRANSPORT]

        async def send(self, request, **kwargs):
            request = request_type('GET', 'http://127.0.0.1/')
            if hasattr(response_type, "content"):
                response = response_type(request=request, internal_response=None)
            else:
                response = response_type(request, None)
            response.status_code = 200
            return response

    class MockContent():
        def __init__(self):
            self._first = True

        async def read(self, block_size):
            if self._first:
                self._first = False
                raise ConnectionError
            return None

    class MockInternalResponse():
        def __init__(self):
            self.headers = {}
            self.content = MockContent()

        async def close(self):
            pass

    class AsyncMock(mock.MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)

    http_request = request_type('GET', 'http://127.0.0.1/')
    pipeline = AsyncPipeline(MockTransport())
    if hasattr(response_type, "content"):
        http_response = response_type(request=http_request, internal_response=None)
    else:
        http_response = response_type(http_request, None)
    http_response.internal_response = MockInternalResponse()
    stream = AioHttpStreamDownloadGenerator(pipeline, http_response, decompress=False)
    with mock.patch('asyncio.sleep', new_callable=AsyncMock):
        with pytest.raises(ConnectionError):
            await stream.__anext__()

@pytest.mark.asyncio
@pytest.mark.parametrize("response_type", [PipelineTransportAsyncioRequestsTransportResponse, RestAsyncioRequestsTransportResponse])
async def test_response_streaming_error_behavior(response_type):
    # Test to reproduce https://github.com/Azure/azure-sdk-for-python/issues/16723
    block_size = 103
    total_response_size = 500
    req_response = requests.Response()
    req_request = requests.Request()

    class FakeStreamWithConnectionError:
        # fake object for urllib3.response.HTTPResponse
        def __init__(self):
            self.total_response_size = 500

        def stream(self, chunk_size, decode_content=False):
            assert chunk_size == block_size
            left = total_response_size
            while left > 0:
                if left <= block_size:
                    raise requests.exceptions.ConnectionError()
                data = b"X" * min(chunk_size, left)
                left -= len(data)
                yield data

        def read(self, chunk_size, decode_content=False):
            assert chunk_size == block_size
            if self.total_response_size > 0:
                if self.total_response_size <= block_size:
                    raise requests.exceptions.ConnectionError()
                data = b"X" * min(chunk_size, self.total_response_size)
                self.total_response_size -= len(data)
                return data

        def close(self):
            pass

    req_response.raw = FakeStreamWithConnectionError()

    if hasattr(response_type, "content"):
        response = response_type(
            request=req_request,
            internal_response=req_response,
        )
        response._connection_data_block_size = block_size
    else:
        response = response_type(
            req_request,
            req_response,
            block_size,
        )

    async def mock_run(self, *args, **kwargs):
        return PipelineResponse(
            None,
            requests.Response(),
            None,
        )

    transport = AioHttpTransport()
    pipeline = AsyncPipeline(transport)
    pipeline.run = mock_run
    if hasattr(response_type, "iter_bytes"):
        # iter_bytes corresponds to iterating with decopression
        downloader = response.iter_bytes()
    else:
        downloader = response.stream_download(pipeline)
    with pytest.raises(requests.exceptions.ConnectionError):
        while True:
            await downloader.__anext__()
