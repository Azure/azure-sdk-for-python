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
import pytest
import trio


@pytest.fixture(params=[True, False])
def stream(request):
    return request.param


@pytest.mark.asyncio
async def test_async_requests_transport_short_read_raises(port, stream):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(Exception, match="IncompleteRead"):
        async with AsyncPipeline(AsyncioRequestsTransport()) as pipeline:
            response = await pipeline.run(request, stream=stream)
            assert response.http_response.status_code == 200
            await response.http_response.body()


def test_trio_transport_short_read_raises(port, stream):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))

    async def do():
        with pytest.raises(Exception, match="IncompleteRead"):
            async with AsyncPipeline(TrioRequestsTransport()) as pipeline:
                response = await pipeline.run(request, stream=stream)
                assert response.http_response.status_code == 200
                await response.http_response.body()

    trio.run(do)


@pytest.mark.asyncio
async def test_aio_transport_short_read_raises(port, stream):
    request = HttpRequest("GET", "http://localhost:{}/errors/short-data".format(port))
    with pytest.raises(Exception, match="payload is not completed"):
        async with AsyncPipeline(AioHttpTransport()) as pipeline:
            response = await pipeline.run(request, stream=stream)
            assert response.http_response.status_code == 200
            await response.http_response.load_body()
