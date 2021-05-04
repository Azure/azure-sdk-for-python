# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import requests
from azure.core.pipeline.transport import (
    HttpRequest,
    AsyncHttpResponse,
    AsyncHttpTransport,
    AsyncioRequestsTransportResponse,
    AioHttpTransport,
)
from azure.core.pipeline import AsyncPipeline, PipelineResponse
from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator
from unittest import mock
import pytest

@pytest.mark.asyncio
async def test_connection_error_response():
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._count = 0

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def close(self):
            pass
        async def open(self):
            pass

        async def send(self, request, **kwargs):
            request = HttpRequest('GET', 'http://127.0.0.1/')
            response = AsyncHttpResponse(request, None)
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

    http_request = HttpRequest('GET', 'http://127.0.0.1/')
    pipeline = AsyncPipeline(MockTransport())
    http_response = AsyncHttpResponse(http_request, None)
    http_response.internal_response = MockInternalResponse()
    stream = AioHttpStreamDownloadGenerator(pipeline, http_response)
    with mock.patch('asyncio.sleep', new_callable=AsyncMock):
        with pytest.raises(ConnectionError):
            await stream.__anext__()

@pytest.mark.asyncio
async def test_response_streaming_error_behavior():
    # Test to reproduce https://github.com/Azure/azure-sdk-for-python/issues/16723
    block_size = 103
    total_response_size = 500
    req_response = requests.Response()
    req_request = requests.Request()

    class FakeStreamWithConnectionError:
        # fake object for urllib3.response.HTTPResponse

        def stream(self, chunk_size, decode_content=False):
            assert chunk_size == block_size
            left = total_response_size
            while left > 0:
                if left <= block_size:
                    raise requests.exceptions.ConnectionError()
                data = b"X" * min(chunk_size, left)
                left -= len(data)
                yield data

        def close(self):
            pass

    req_response.raw = FakeStreamWithConnectionError()

    response = AsyncioRequestsTransportResponse(
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
    downloader = response.stream_download(pipeline)
    with pytest.raises(requests.exceptions.ConnectionError):
        while True:
            await downloader.__anext__()
