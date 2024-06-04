# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from corehttp.exceptions import HttpResponseError, ServiceRequestError
from corehttp.rest import HttpRequest
from corehttp.exceptions import StreamClosedError, StreamConsumedError, ResponseNotReadError

from rest_client_async import AsyncMockRestClient
from utils import ASYNC_TRANSPORTS


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_iter_raw(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_iter_raw_on_iterable(port, transport):
    request = HttpRequest("GET", "/streams/iterable")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_iter_with_error(port, transport):
    request = HttpRequest("GET", "/errors/403")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        try:
            response.raise_for_status()
        except HttpResponseError as e:
            pass
    assert response.is_closed

    try:
        async with client.send_request(request, stream=True) as response:
            response.raise_for_status()
    except HttpResponseError as e:
        pass

    assert response.is_closed

    request = HttpRequest("GET", "http://doesNotExist")
    with pytest.raises(ServiceRequestError):
        async with await client.send_request(request, stream=True):
            raise ValueError("Should error before entering")
    assert response.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_iter_bytes(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for chunk in response.iter_bytes():
            assert response.is_stream_consumed
            assert not response.is_closed
            raw += chunk
        assert response.is_stream_consumed
        assert response.is_closed
        assert raw == b"Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_streaming_response(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = await response.read()
        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_cannot_read_after_stream_consumed(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        content = b""
        async for chunk in response.iter_bytes():
            content += chunk

        with pytest.raises(StreamConsumedError) as ex:
            await response.read()
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "You have likely already consumed this stream, so it can not be accessed anymore" in str(ex.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_cannot_read_after_response_closed(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        pass

    with pytest.raises(StreamClosedError) as ex:
        await response.read()
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "can no longer be read or streamed, since the response has already been closed" in str(ex.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_iter_read_back_and_forth(port, transport):
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "/basic/string")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        async for part in response.iter_bytes():
            assert part
        with pytest.raises(ResponseNotReadError):
            response.text()
        with pytest.raises(StreamConsumedError):
            await response.read()
        with pytest.raises(ResponseNotReadError):
            response.text()


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_error_reading(port, transport):
    request = HttpRequest("GET", "/errors/403")
    client = AsyncMockRestClient(port, transport=transport())
    async with client.send_request(request, stream=True) as response:
        await response.read()
        assert response.content == b""
    response.content

    response = await client.send_request(request, stream=True)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()
    await response.read()
    assert response.content == b""
    await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_pass_kwarg_to_iter_bytes(port, transport):
    request = HttpRequest("GET", "/basic/string")
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(request, stream=True)
    async for part in response.iter_bytes(chunk_size=5):
        assert part


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_pass_kwarg_to_iter_raw(port, transport):
    request = HttpRequest("GET", "/basic/string")
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(request, stream=True)
    async for part in response.iter_raw(chunk_size=5):
        assert part


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_header(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(request)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_deflate_decompress_compressed_header(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/deflate")
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(request)
    content = await response.read()
    assert content == b"hi there"
    assert response.content == content
    assert response.text() == "hi there"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_decompress_compressed_header_stream(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(request, stream=True)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"
