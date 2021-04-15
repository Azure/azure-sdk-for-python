# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import json
import pytest
from azure.core.rest import AsyncHttpResponse, HttpRequest, ResponseClosedError, StreamConsumedError
from azure.core.pipeline.transport import AioHttpTransport

HTTPBIN_JPEG_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "httpbin.jpeg"))

async def _create_http_response(url, content=None):
    # type: (int, Any, Dict[str, Any], bytes) -> AsyncHttpResponse
    # https://github.com/psf/requests/blob/67a7b2e8336951d527e223429672354989384197/requests/adapters.py#L255

    request = HttpRequest(
        method="GET",
        url=url,
    )

    internal_response = await AioHttpTransport().send(request._internal_request, stream=True)
    return AsyncHttpResponse(
        request=request,
        _internal_response=internal_response
    )

def _read_jpeg_file():
    with open(HTTPBIN_JPEG_FILE_NAME, "rb") as f:
        file_bytes = f.read()
    return file_bytes

def _assert_stream_state(response, open):
    # if open is true, check the stream is open.
    # if false, check if everything is closed
    checks = [
        response.is_closed,
        response.is_stream_consumed
    ]
    if open:
        assert not any(checks)
    else:
        assert all(checks)

@pytest.mark.asyncio
async def test_iter_raw():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")
    raw = b""
    async for chunk in response.iter_raw():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

async def _iter_raw_with_chunk_size_helper(chunk_size):
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")
    raw = b""
    async for chunk in response.iter_raw(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

@pytest.mark.asyncio
async def test_iter_raw_with_chunk_size():
    await _iter_raw_with_chunk_size_helper(chunk_size=5)
    await _iter_raw_with_chunk_size_helper(chunk_size=13)
    await _iter_raw_with_chunk_size_helper(chunk_size=20)

@pytest.mark.asyncio
async def test_iter_raw_num_bytes_downloaded():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")

    num_downloaded = response.num_bytes_downloaded
    async for chunk in response.iter_raw():
        assert len(chunk) == (response.num_bytes_downloaded - num_downloaded)
        num_downloaded = response.num_bytes_downloaded

async def _iter_bytes_with_chunk_size_helper(chunk_size):
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")
    raw = b""
    async for chunk in response.iter_bytes(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

@pytest.mark.asyncio
async def test_iter_bytes():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")
    raw = b""
    async for chunk in response.iter_bytes():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

@pytest.mark.asyncio
async def test_iter_bytes_with_chunk_size():
    await _iter_bytes_with_chunk_size_helper(chunk_size=5)
    await _iter_bytes_with_chunk_size_helper(chunk_size=13)
    await _iter_bytes_with_chunk_size_helper(chunk_size=20)

@pytest.mark.asyncio
async def test_iter_text():
    response = await _create_http_response(url="https://httpbin.org/stream/10")
    raw = ""
    async for chunk in response.iter_text():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    # just going to verify that we got 10 stream chunks from the url
    assert len([r for r in raw.split("\n") if r]) == 10

async def _iter_text_with_chunk_size_helper(chunk_size):
    response = await _create_http_response(url="https://httpbin.org/stream/10")
    raw = ""
    async for chunk in response.iter_text(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert len([r for r in raw.split("\n") if r]) == 10

@pytest.mark.asyncio
async def test_iter_text_with_chunk_size():
    await _iter_text_with_chunk_size_helper(chunk_size=5)
    await _iter_text_with_chunk_size_helper(chunk_size=13)
    await _iter_text_with_chunk_size_helper(chunk_size=20)

@pytest.mark.asyncio
async def test_iter_lines():
    response = await _create_http_response(url="https://httpbin.org/stream/10")
    lines = []
    async for chunk in response.iter_lines():
        _assert_stream_state(response, open=True)
        lines.append(chunk)
    _assert_stream_state(response, open=False)
    assert len(lines) == 10

    for idx, line in enumerate(lines):
        assert json.loads(line)['id'] == idx
        assert line[-1] == "\n"


@pytest.mark.asyncio
async def test_sync_streaming_response():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")

    assert response.status_code == 200
    assert not response.is_closed

    content = await response.read()

    with open(HTTPBIN_JPEG_FILE_NAME, "rb") as f:
        file_bytes = f.read()
    assert content == file_bytes
    assert response.content == file_bytes
    assert response.is_closed


@pytest.mark.asyncio
async def test_cannot_read_after_stream_consumed():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")

    content = b""
    async for chunk in response.iter_bytes():
        content += chunk

    with pytest.raises(ResponseClosedError) as ex:
        await response.read()
    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)

@pytest.mark.asyncio
async def test_cannot_read_after_response_closed():
    response = await _create_http_response(url="https://httpbin.org/image/jpeg")

    await response.close()
    with pytest.raises(ResponseClosedError) as ex:
        await response.read()
    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)
