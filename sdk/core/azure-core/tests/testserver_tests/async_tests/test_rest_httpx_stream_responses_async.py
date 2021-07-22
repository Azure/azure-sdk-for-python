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
from azure.core.rest import HttpRequest
from azure.core.exceptions import StreamClosedError, StreamConsumedError, ResponseNotReadError

@pytest.mark.asyncio
async def test_iter_with_error(httpx_client):
    request = HttpRequest("GET", "/errors/403")

    async with httpx_client.send_request(request, stream=True) as response:
        try:
            response.raise_for_status()
        except HttpResponseError as e:
            pass
    assert response.is_closed

    try:
        async with httpx_client.send_request(request, stream=True) as response:
            response.raise_for_status()
    except HttpResponseError as e:
        pass

    assert response.is_closed

    request = HttpRequest("GET", "http://doesNotExist")
    with pytest.raises(ServiceRequestError):
        async with (await httpx_client.send_request(request, stream=True)):
            raise ValueError("Should error before entering")
    assert response.is_closed

@pytest.mark.asyncio
async def test_iter_text(httpx_client):
    request = HttpRequest("GET", "/basic/string")

    async with httpx_client.send_request(request, stream=True) as response:
        content = ""
        async for part in response.iter_text():
            content += part
        assert content == "Hello, world!"

@pytest.mark.asyncio
async def test_iter_lines(httpx_client):
    request = HttpRequest("GET", "/basic/lines")

    async with httpx_client.send_request(request, stream=True) as response:
        content = []
        async for line in response.iter_lines():
            content.append(line)
        assert content == ["Hello,\n", "world!"]

@pytest.mark.asyncio
async def test_cannot_read_after_response_closed(port, httpx_client):
    request = HttpRequest("GET", "/streams/basic")
    async with httpx_client.send_request(request, stream=True) as response:
        pass

    with pytest.raises(StreamClosedError) as ex:
        await response.read()
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "can no longer be read or streamed, since the response has already been closed" in str(ex.value)

@pytest.mark.asyncio
async def test_decompress_plain_no_header(httpx_client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    async with httpx_client:
        response = await httpx_client.send_request(request, stream=True)
        with pytest.raises(ResponseNotReadError):
            response.content
        await response.read()
        assert response.content == b"test"

@pytest.mark.asyncio
async def test_compress_plain_no_header(httpx_client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    async with httpx_client:
        response = await httpx_client.send_request(request, stream=True)
        iter = response.iter_raw()
        data = b""
        async for d in iter:
            data += d
        assert data == b"test"

@pytest.mark.asyncio
async def test_iter_read_back_and_forth(httpx_client):
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "/basic/lines")

    async with httpx_client.send_request(request, stream=True) as response:
        async for line in response.iter_lines():
            assert line
        with pytest.raises(ResponseNotReadError):
            response.text
        with pytest.raises(StreamConsumedError):
            await response.read()
        with pytest.raises(ResponseNotReadError):
            response.text

@pytest.mark.asyncio
async def test_stream_with_return_pipeline_response(httpx_client):
    request = HttpRequest("GET", "/basic/lines")
    pipeline_response = await httpx_client.send_request(request, stream=True, _return_pipeline_response=True)
    assert hasattr(pipeline_response, "http_request")
    assert hasattr(pipeline_response.http_request, "content")
    assert hasattr(pipeline_response, "http_response")
    assert hasattr(pipeline_response, "context")
    parts = []
    async for line in pipeline_response.http_response.iter_lines():
        parts.append(line)
    assert parts == ['Hello,\n', 'world!']
    await httpx_client.close()

@pytest.mark.asyncio
async def test_error_reading(httpx_client):
    request = HttpRequest("GET", "/errors/403")
    async with httpx_client.send_request(request, stream=True) as response:
        await response.read()
        assert response.content == b""
    response.content

    response = await httpx_client.send_request(request, stream=True)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()
    await response.read()
    assert response.content == b""
    await httpx_client.close()
