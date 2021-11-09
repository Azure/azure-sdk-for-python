# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError, ServiceRequestError
import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import StreamClosedError, StreamConsumedError, ResponseNotReadError

@pytest.mark.asyncio
async def test_iter_raw(client):
    request = HttpRequest("GET", "/streams/basic")
    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

@pytest.mark.asyncio
async def test_iter_raw_on_iterable(client):
    request = HttpRequest("GET", "/streams/iterable")

    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

@pytest.mark.asyncio
async def test_iter_with_error(client):
    request = HttpRequest("GET", "/errors/403")

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
async def test_iter_bytes(client):
    request = HttpRequest("GET", "/streams/basic")

    async with client.send_request(request, stream=True) as response:
        raw = b""
        async for chunk in response.iter_bytes():
            assert response.is_stream_consumed
            assert not response.is_closed
            raw += chunk
        assert response.is_stream_consumed
        assert response.is_closed
        assert raw == b"Hello, world!"

@pytest.mark.skip(reason="We've gotten rid of iter_text for now")
@pytest.mark.asyncio
async def test_iter_text(client):
    request = HttpRequest("GET", "/basic/string")

    async with client.send_request(request, stream=True) as response:
        content = ""
        async for part in response.iter_text():
            content += part
        assert content == "Hello, world!"

@pytest.mark.skip(reason="We've gotten rid of iter_lines for now")
@pytest.mark.asyncio
async def test_iter_lines(client):
    request = HttpRequest("GET", "/basic/lines")

    async with client.send_request(request, stream=True) as response:
        content = []
        async for part in response.iter_lines():
            content.append(part)
        assert content == ["Hello,\n", "world!"]


@pytest.mark.asyncio
async def test_streaming_response(client):
    request = HttpRequest("GET", "/streams/basic")

    async with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = await response.read()
        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed

@pytest.mark.asyncio
async def test_cannot_read_after_stream_consumed(port, client):
    request = HttpRequest("GET", "/streams/basic")
    async with client.send_request(request, stream=True) as response:
        content = b""
        async for chunk in response.iter_bytes():
            content += chunk

        with pytest.raises(StreamConsumedError) as ex:
            await response.read()
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "You have likely already consumed this stream, so it can not be accessed anymore" in str(ex.value)


@pytest.mark.asyncio
async def test_cannot_read_after_response_closed(port, client):
    request = HttpRequest("GET", "/streams/basic")
    async with client.send_request(request, stream=True) as response:
        pass

    with pytest.raises(StreamClosedError) as ex:
        await response.read()
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "can no longer be read or streamed, since the response has already been closed" in str(ex.value)

@pytest.mark.asyncio
async def test_decompress_plain_no_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    async with client:
        response = await client.send_request(request, stream=True)
        with pytest.raises(ResponseNotReadError):
            response.content
        await response.read()
        assert response.content == b"test"

@pytest.mark.asyncio
async def test_compress_plain_no_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    async with client:
        response = await client.send_request(request, stream=True)
        iter = response.iter_raw()
        data = b""
        async for d in iter:
            data += d
        assert data == b"test"

@pytest.mark.asyncio
async def test_iter_read_back_and_forth(client):
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "/basic/string")

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
async def test_stream_with_return_pipeline_response(client):
    request = HttpRequest("GET", "/basic/string")
    pipeline_response = await client.send_request(request, stream=True, _return_pipeline_response=True)
    assert hasattr(pipeline_response, "http_request")
    assert hasattr(pipeline_response.http_request, "content")
    assert hasattr(pipeline_response, "http_response")
    assert hasattr(pipeline_response, "context")
    parts = []
    async for part in pipeline_response.http_response.iter_bytes():
        parts.append(part)
    assert parts == [b'Hello, world!']
    await client.close()

@pytest.mark.asyncio
async def test_error_reading(client):
    request = HttpRequest("GET", "/errors/403")
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
async def test_pass_kwarg_to_iter_bytes(client):
    request = HttpRequest("GET", "/basic/string")
    response = await client.send_request(request, stream=True)
    async for part in response.iter_bytes(chunk_size=5):
        assert part

@pytest.mark.asyncio
async def test_pass_kwarg_to_iter_raw(client):
    request = HttpRequest("GET", "/basic/string")
    response = await client.send_request(request, stream=True)
    async for part in response.iter_raw(chunk_size=5):
        assert part

@pytest.mark.asyncio
async def test_decompress_compressed_header(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

@pytest.mark.asyncio
async def test_decompress_compressed_header_stream(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request, stream=True)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

@pytest.mark.asyncio
async def test_decompress_compressed_header_stream_body_content(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request, stream=True)
    await response.read()
    content = response.content
    assert content == response.body()
