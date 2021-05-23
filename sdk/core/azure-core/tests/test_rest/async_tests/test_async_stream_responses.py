# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import functools
import os
import json
import pytest
from azure.core.rest import AsyncHttpResponse, HttpRequest, ResponseClosedError, StreamConsumedError

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
async def test_iter_raw(async_client):
    request = HttpRequest("GET", "http://127.0.0.1:5000/streams/basic")
    async with async_client.send_request(request, stream_response=True) as response:
        raw = b""
        for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

# def test_iter_raw_on_iterable(async_client):
#     request = HttpRequest("GET", "http://127.0.0.1:5000/streams/iterable")

#     with async_client.send_request(request, stream_response=True) as response:
#         raw = b""
#         for part in response.iter_raw():
#             raw += part
#         assert raw == b"Hello, world!"
# @pytest.mark.asyncio
# async def test_iter_raw_with_chunk_size(send_request):
#     await _iter_raw_with_chunk_size_helper(chunk_size=5, send_request=send_request)
#     await _iter_raw_with_chunk_size_helper(chunk_size=13, send_request=send_request)
#     await _iter_raw_with_chunk_size_helper(chunk_size=20, send_request=send_request)

# @pytest.mark.asyncio
# async def test_iter_raw_num_bytes_downloaded(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

#     num_downloaded = response.num_bytes_downloaded
#     async for chunk in response.iter_raw():
#         assert len(chunk) == (response.num_bytes_downloaded - num_downloaded)
#         num_downloaded = response.num_bytes_downloaded

# async def _iter_bytes_with_chunk_size_helper(chunk_size, send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))
#     raw = b""
#     async for chunk in response.iter_bytes(chunk_size=chunk_size):
#         _assert_stream_state(response, open=True)
#         raw += chunk
#         assert len(chunk) <= chunk_size
#     _assert_stream_state(response, open=False)
#     assert raw == _read_jpeg_file()

# @pytest.mark.asyncio
# async def test_iter_bytes(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))
#     raw = b""
#     async for chunk in response.iter_bytes():
#         _assert_stream_state(response, open=True)
#         raw += chunk
#     _assert_stream_state(response, open=False)
#     assert raw == _read_jpeg_file()

# @pytest.mark.asyncio
# async def test_iter_bytes_with_chunk_size(send_request):
#     await _iter_bytes_with_chunk_size_helper(chunk_size=5, send_request=send_request)
#     await _iter_bytes_with_chunk_size_helper(chunk_size=13, send_request=send_request)
#     await _iter_bytes_with_chunk_size_helper(chunk_size=20, send_request=send_request)

# @pytest.mark.asyncio
# async def test_iter_text(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/text"))
#     raw = ""
#     async for chunk in response.iter_text():
#         _assert_stream_state(response, open=True)
#         raw += chunk
#     _assert_stream_state(response, open=False)
#     # just going to verify that we got 10 stream chunks from the url
#     assert len([r for r in raw.split("\n") if r]) == 10

# async def _iter_text_with_chunk_size_helper(chunk_size, send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/text"))
#     raw = ""
#     async for chunk in response.iter_text(chunk_size=chunk_size):
#         _assert_stream_state(response, open=True)
#         raw += chunk
#         assert len(chunk) <= chunk_size
#     _assert_stream_state(response, open=False)
#     assert len([r for r in raw.split("\n") if r]) == 10

# @pytest.mark.asyncio
# async def test_iter_text_with_chunk_size(send_request):
#     await _iter_text_with_chunk_size_helper(chunk_size=5, send_request=send_request)
#     await _iter_text_with_chunk_size_helper(chunk_size=13, send_request=send_request)
#     await _iter_text_with_chunk_size_helper(chunk_size=20, send_request=send_request)

# @pytest.mark.asyncio
# async def test_iter_lines(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/text"))
#     lines = []
#     async for chunk in response.iter_lines():
#         _assert_stream_state(response, open=True)
#         lines.append(chunk)
#     _assert_stream_state(response, open=False)
#     assert len(lines) == 10
#     for line in lines:
#         assert line == "Hello, world!\n"


# @pytest.mark.asyncio
# async def test_sync_streaming_response(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

#     assert response.status_code == 200
#     assert not response.is_closed

#     content = await response.read()

#     with open(HTTPBIN_JPEG_FILE_NAME, "rb") as f:
#         file_bytes = f.read()
#     assert content == file_bytes
#     assert response.content == file_bytes
#     assert response.is_closed


# @pytest.mark.asyncio
# async def test_cannot_read_after_stream_consumed(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

#     content = b""
#     async for chunk in response.iter_bytes():
#         content += chunk

#     with pytest.raises(ResponseClosedError) as ex:
#         await response.read()
#     assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)

# @pytest.mark.asyncio
# async def test_cannot_read_after_response_closed(send_request):
#     response = await send_request(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

#     await response.close()
#     with pytest.raises(ResponseClosedError) as ex:
#         await response.read()
#     assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)
