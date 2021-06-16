# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError, ServiceRequestError
import functools
import os
import json
import pytest
from azure.core.rest import StreamConsumedError, HttpRequest, StreamClosedError, StreamConsumedError

@pytest.mark.asyncio
async def test_iter_raw(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")
    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

@pytest.mark.asyncio
async def test_iter_raw_on_iterable(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/iterable")

    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

@pytest.mark.asyncio
async def test_iter_with_error(client):
    request = HttpRequest("GET", "http://localhost:5000/errors/403")

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
        async with (await client.send_request(request, stream=True)):
            raise ValueError("Should error before entering")
    assert response.is_closed

@pytest.mark.asyncio
async def test_iter_raw_with_chunksize(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_raw(chunk_size=5):
            parts.append(part)
        assert parts == [b"Hello", b", wor", b"ld!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_raw(chunk_size=13):
            parts.append(part)
        assert parts == [b"Hello, world!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_raw(chunk_size=20):
            parts.append(part)
        assert parts == [b"Hello, world!"]

@pytest.mark.asyncio
async def test_iter_raw_num_bytes_downloaded(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    async with client.send_request(request, stream=True) as response:
        num_downloaded = response.num_bytes_downloaded
        async for part in response.iter_raw():
            assert len(part) == (response.num_bytes_downloaded - num_downloaded)
            num_downloaded = response.num_bytes_downloaded

@pytest.mark.asyncio
async def test_iter_bytes(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

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
async def test_iter_bytes_with_chunk_size(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_bytes(chunk_size=5):
            parts.append(part)
        assert parts == [b"Hello", b", wor", b"ld!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_bytes(chunk_size=13):
            parts.append(part)
        assert parts == [b"Hello, world!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_bytes(chunk_size=20):
            parts.append(part)
        assert parts == [b"Hello, world!"]

@pytest.mark.asyncio
async def test_iter_text(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/string")

    async with client.send_request(request, stream=True) as response:
        content = ""
        async for part in response.iter_text():
            content += part
        assert content == "Hello, world!"

@pytest.mark.asyncio
async def test_iter_text_with_chunk_size(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/string")

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_text(chunk_size=5):
            parts.append(part)
        assert parts == ["Hello", ", wor", "ld!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_text(chunk_size=13):
            parts.append(part)
        assert parts == ["Hello, world!"]

    async with client.send_request(request, stream=True) as response:
        parts = []
        async for part in response.iter_text(chunk_size=20):
            parts.append(part)
        assert parts == ["Hello, world!"]

@pytest.mark.asyncio
async def test_iter_lines(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/lines")

    async with client.send_request(request, stream=True) as response:
        content = []
        async for line in response.iter_lines():
            content.append(line)
        assert content == ["Hello,\n", "world!"]


@pytest.mark.asyncio
async def test_streaming_response(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    async with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = await response.read()

        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed

@pytest.mark.asyncio
async def test_cannot_read_after_stream_consumed(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")
    async with client.send_request(request, stream=True) as response:
        content = b""
        async for chunk in response.iter_bytes():
            content += chunk

        with pytest.raises(StreamConsumedError) as ex:
            await response.read()
    assert "You are attempting to read or stream content that has already been streamed" in str(ex.value)

@pytest.mark.asyncio
async def test_cannot_read_after_response_closed(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")
    async with client.send_request(request, stream=True) as response:
        pass

    with pytest.raises(StreamClosedError) as ex:
        await response.read()
    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)
