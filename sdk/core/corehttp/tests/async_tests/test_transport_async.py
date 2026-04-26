# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from unittest import mock
import asyncio
from packaging.version import Version

import httpx
from corehttp.rest import HttpRequest
from corehttp.transport.aiohttp import AioHttpTransport
from corehttp.transport.httpx import AsyncHttpXTransport
from corehttp.runtime.pipeline import AsyncPipeline
from corehttp.exceptions import (
    ServiceResponseError,
    ServiceRequestError,
    ServiceRequestTimeoutError,
    ServiceResponseTimeoutError,
)

import aiohttp
import pytest


class MockAioHttpSession:
    auto_decompress = False

    def __init__(self):
        self.request = mock.AsyncMock(side_effect=RuntimeError("request sent"))

    async def __aenter__(self):
        return self

    async def close(self):
        pass


def _make_async_httpx_client_mock():
    client = mock.create_autospec(httpx.AsyncClient, instance=True)
    client.request.side_effect = RuntimeError("request sent")
    return client


@pytest.mark.asyncio
async def test_aiohttp_transport_rejects_unknown_kwargs():
    session = MockAioHttpSession()
    transport = AioHttpTransport(session=session, session_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(TypeError, match=r"AioHttpTransport\.send\(\) got an unexpected keyword argument 'query_filter'"):
        await transport.send(request, query_filter="PartitionKey eq 'pk001'")

    session.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_async_pipeline_aiohttp_transport_rejects_unknown_kwargs():
    session = MockAioHttpSession()
    transport = AioHttpTransport(session=session, session_owner=False)
    pipeline = AsyncPipeline(transport)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(TypeError, match=r"AioHttpTransport\.send\(\) got an unexpected keyword argument 'query_filter'"):
        await pipeline.run(request, query_filter="PartitionKey eq 'pk001'")

    session.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_aiohttp_transport_consumes_supported_kwargs():
    session = MockAioHttpSession()
    transport = AioHttpTransport(session=session, session_owner=False)
    request = HttpRequest("GET", "https://localhost")

    with pytest.raises(RuntimeError, match="request sent"):
        await transport.send(
            request,
            stream=True,
            proxy="http://proxy",
            connection_timeout=1,
            read_timeout=2,
            connection_verify=False,
            connection_cert=None,
        )

    kwargs = session.request.await_args.kwargs
    assert kwargs["proxy"] == "http://proxy"
    assert kwargs["timeout"].sock_connect == 1
    assert kwargs["timeout"].sock_read == 2
    assert "connection_timeout" not in kwargs
    assert "read_timeout" not in kwargs
    assert "connection_verify" not in kwargs
    assert "connection_cert" not in kwargs


@pytest.mark.asyncio
async def test_httpx_transport_rejects_unknown_kwargs():
    client = _make_async_httpx_client_mock()
    transport = AsyncHttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(
        TypeError, match=r"AsyncHttpXTransport\.send\(\) got an unexpected keyword argument 'query_filter'"
    ):
        await transport.send(request, query_filter="PartitionKey eq 'pk001'")

    client.request.assert_not_awaited()


@pytest.mark.parametrize("tls_kwarg", ["connection_verify", "connection_cert"])
@pytest.mark.asyncio
async def test_httpx_transport_rejects_per_request_tls_kwargs(tls_kwarg):
    client = _make_async_httpx_client_mock()
    transport = AsyncHttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(
        TypeError, match=f"AsyncHttpXTransport.send\\(\\) got an unexpected keyword argument '{tls_kwarg}'"
    ):
        await transport.send(request, **{tls_kwarg: "cert.pem"})

    client.request.assert_not_awaited()


@pytest.mark.asyncio
async def test_httpx_transport_consumes_supported_kwargs():
    client = _make_async_httpx_client_mock()
    transport = AsyncHttpXTransport(client=client, client_owner=False)
    request = HttpRequest("GET", "http://localhost")

    with pytest.raises(RuntimeError, match="request sent"):
        await transport.send(
            request,
            connection_timeout=1,
            read_timeout=2,
        )

    kwargs = client.request.await_args.kwargs
    assert kwargs["timeout"].connect == 1
    assert kwargs["timeout"].read == 2
    assert "connection_timeout" not in kwargs
    assert "read_timeout" not in kwargs


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
