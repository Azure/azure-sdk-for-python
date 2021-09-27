# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import (
    HttpRequest,
    AsyncioRequestsTransport,
    TrioRequestsTransport,
    AioHttpTransport,
)
from azure.core import AsyncPipelineClient
from azure.core.exceptions import IncompleteReadError
import pytest
import trio


@pytest.fixture(params=[True, False])
def stream(request):
    return request.param


@pytest.mark.asyncio
async def test_async_requests_transport_short_read_raises(port):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(IncompleteReadError):
        async with AsyncPipeline(AsyncioRequestsTransport()) as pipeline:
            response = await pipeline.run(request, stream=False)
            assert response.http_response.status_code == 200


def test_trio_transport_short_read_raises(port):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))

    async def do():
        with pytest.raises(IncompleteReadError):
            async with AsyncPipeline(TrioRequestsTransport()) as pipeline:
                response = await pipeline.run(request, stream=False)
                assert response.http_response.status_code == 200

    trio.run(do)


@pytest.mark.asyncio
async def test_aio_transport_short_read_raises(port, stream):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(IncompleteReadError):
        async with AsyncPipeline(AioHttpTransport()) as pipeline:
            response = await pipeline.run(request, stream=stream)
            assert response.http_response.status_code == 200
            await response.http_response.load_body()


@pytest.mark.asyncio
async def test_aio_transport_short_read_download_stream(port):
    url = "http://localhost:{}/errors/short-data".format(port)
    client = AsyncPipelineClient(url)
    with pytest.raises(IncompleteReadError):
        async with client:
            request = HttpRequest("GET", url)
            pipeline_response = await client._pipeline.run(request, stream=True)
            response = pipeline_response.http_response
            data = response.stream_download(client._pipeline)
            content = b""
            async for d in data:
                content += d
