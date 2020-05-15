# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.core.pipeline.transport import (
    HttpRequest,
    AsyncHttpResponse,
    AsyncHttpTransport,
)
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport._aiohttp import AioHttpStreamDownloadGenerator
from unittest import mock
import pytest

@pytest.mark.asyncio
async def test_connetion_error_response():
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
            response.status_code = 416
            return response

    class MockContent():
        async def read(self, block_size):
            raise ConnectionError

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
