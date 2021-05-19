# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import functools
import os
from typing import Type
import pytest
from azure.core.rest import HttpResponse, HttpRequest, StreamConsumedError, ResponseClosedError
from azure.core.pipeline.transport import RequestsTransport
from testcase import _create_http_response

HTTPBIN_JPEG_FILE_NAME = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "httpbin.jpeg"))

create_http_response = functools.partial(_create_http_response, stream=True)

def _read_jpeg_file():
    with open(HTTPBIN_JPEG_FILE_NAME, "rb") as f:
        file_bytes = f.read()
    return file_bytes

def _assert_stream_state(response, open):
    # if open is true, check the stream is open.
    # if false, check if everything is closed
    checks = [
        response._internal_response.internal_response._content_consumed,
        response.is_closed,
        response.is_stream_consumed
    ]
    if open:
        assert not any(checks)
    else:
        assert all(checks)

def test_iter_raw():
    response = create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/streams/jpeg"),
    )
    raw = b""
    for chunk in response.iter_raw():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

def _iter_raw_with_chunk_size_helper(chunk_size):
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))
    raw = b""
    for chunk in response.iter_raw(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

def test_iter_raw_with_chunk_size():
    _iter_raw_with_chunk_size_helper(chunk_size=5)
    _iter_raw_with_chunk_size_helper(chunk_size=13)
    _iter_raw_with_chunk_size_helper(chunk_size=20)

def test_iter_raw_num_bytes_downloaded():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

    num_downloaded = response.num_bytes_downloaded
    for part in response.iter_raw():
        assert len(part) == (response.num_bytes_downloaded - num_downloaded)
        num_downloaded = response.num_bytes_downloaded

def _iter_bytes_with_chunk_size_helper(chunk_size):
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))
    raw = b""
    for chunk in response.iter_bytes(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

def test_iter_bytes():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))
    raw = b""
    for chunk in response.iter_bytes():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    assert raw == _read_jpeg_file()

def test_iter_bytes_with_chunk_size():
    _iter_bytes_with_chunk_size_helper(chunk_size=5)
    _iter_bytes_with_chunk_size_helper(chunk_size=13)
    _iter_bytes_with_chunk_size_helper(chunk_size=20)

def test_iter_text():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/text"))
    raw = ""
    for chunk in response.iter_text():
        _assert_stream_state(response, open=True)
        raw += chunk
    _assert_stream_state(response, open=False)
    # just going to verify that we got 10 stream chunks from the url
    assert len([r for r in raw.split("\n") if r]) == 10

def _iter_text_with_chunk_size_helper(chunk_size):
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/text"))
    raw = ""
    for chunk in response.iter_text(chunk_size=chunk_size):
        _assert_stream_state(response, open=True)
        raw += chunk
        assert len(chunk) <= chunk_size
    _assert_stream_state(response, open=False)
    assert len([r for r in raw.split("\n") if r]) == 10

def test_iter_text_with_chunk_size():
    _iter_text_with_chunk_size_helper(chunk_size=5)
    _iter_text_with_chunk_size_helper(chunk_size=13)
    _iter_text_with_chunk_size_helper(chunk_size=20)

def test_iter_lines():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/text"))
    lines = []
    for chunk in response.iter_lines():
        _assert_stream_state(response, open=True)
        lines.append(chunk)
    _assert_stream_state(response, open=False)
    assert len(lines) == 10
    for line in lines:
        assert line == "Hello, world!\n"

def test_sync_streaming_response():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

    assert response.status_code == 200
    assert not response.is_closed

    content = response.read()

    with open(HTTPBIN_JPEG_FILE_NAME, "rb") as f:
        file_bytes = f.read()
    assert content == file_bytes
    assert response.content == file_bytes
    assert response.is_closed

def test_cannot_read_after_stream_consumed():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

    content = b""
    for part in response.iter_bytes():
        content += part

    with pytest.raises(ResponseClosedError) as ex:
        response.read()

    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)

def test_cannot_read_after_response_closed():
    response = create_http_response(HttpRequest("GET", "http://localhost:3000/streams/jpeg"))

    response.close()
    with pytest.raises(ResponseClosedError) as ex:
        response.read()
    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)
