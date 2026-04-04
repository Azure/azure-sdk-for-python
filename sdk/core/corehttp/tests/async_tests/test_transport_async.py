# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from unittest import mock
import asyncio
from packaging.version import Version

from corehttp.rest import HttpRequest
from corehttp.transport.aiohttp import AioHttpTransport
from corehttp.runtime.pipeline import AsyncPipeline
from corehttp.exceptions import (
    ServiceResponseError,
    ServiceRequestError,
    ServiceRequestTimeoutError,
    ServiceResponseTimeoutError,
)

import aiohttp
import pytest


@pytest.mark.asyncio
async def test_already_close_with_with(caplog, port):
    transport = AioHttpTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

    # This is now closed, new requests should fail
    with pytest.raises(ValueError) as err:
        await transport.send(request)
    assert "HTTP transport has already been closed." in str(err)


@pytest.mark.asyncio
async def test_already_close_manually(caplog, port):
    transport = AioHttpTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    await transport.send(request)
    await transport.close()

    # This is now closed, new requests should fail
    with pytest.raises(ValueError) as err:
        await transport.send(request)
    assert "HTTP transport has already been closed." in str(err)


@pytest.mark.asyncio
async def test_close_too_soon_works_fine(caplog, port):
    transport = AioHttpTransport()

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))

    await transport.close()
    result = await transport.send(request)

    assert result  # No exception is good enough here


@pytest.mark.asyncio
async def test_aiohttp_timeout_response(port):
    async with AioHttpTransport() as transport:

        request = HttpRequest("GET", f"http://localhost:{port}/basic/string")

        with mock.patch.object(
            aiohttp.ClientResponse, "start", side_effect=asyncio.TimeoutError("Too slow!")
        ) as mock_method:
            with pytest.raises(ServiceResponseTimeoutError) as err:
                await transport.send(request)

            with pytest.raises(ServiceResponseError) as err:
                await transport.send(request)

            stream_resp = HttpRequest("GET", f"http://localhost:{port}/streams/basic")
            with pytest.raises(ServiceResponseTimeoutError) as err:
                await transport.send(stream_resp, stream=True)

        stream_resp = await transport.send(stream_resp, stream=True)
        with mock.patch.object(
            aiohttp.streams.StreamReader, "read", side_effect=asyncio.TimeoutError("Too slow!")
        ) as mock_method:
            with pytest.raises(ServiceResponseTimeoutError) as err:
                await stream_resp.read()


@pytest.mark.asyncio
async def test_aiohttp_timeout_request():
    async with AioHttpTransport() as transport:
        transport.session._connector.connect = mock.Mock(side_effect=asyncio.TimeoutError("Too slow!"))

        request = HttpRequest("GET", f"http://localhost:12345/basic/string")

        # aiohttp 3.10 introduced separate connection timeout
        if Version(aiohttp.__version__) >= Version("3.10"):
            with pytest.raises(ServiceRequestTimeoutError) as err:
                await transport.send(request)

            with pytest.raises(ServiceRequestError) as err:
                await transport.send(request)

            stream_request = HttpRequest("GET", f"http://localhost:12345/streams/basic")
            with pytest.raises(ServiceRequestTimeoutError) as err:
                await transport.send(stream_request, stream=True)

        else:
            with pytest.raises(ServiceResponseTimeoutError) as err:
                await transport.send(request)

            with pytest.raises(ServiceResponseError) as err:
                await transport.send(request)

            stream_request = HttpRequest("GET", f"http://localhost:12345/streams/basic")
            with pytest.raises(ServiceResponseTimeoutError) as err:
                await transport.send(stream_request, stream=True)
