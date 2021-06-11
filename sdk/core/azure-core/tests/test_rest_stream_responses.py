# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest, ResponseClosedError, StreamConsumedError
from azure.core.exceptions import HttpResponseError, ServiceRequestError

def _assert_stream_state(response, open):
    # if open is true, check the stream is open.
    # if false, check if everything is closed
    checks = [
        response.internal_response._content_consumed,
        response.is_closed,
        response.is_stream_consumed
    ]
    if open:
        assert not any(checks)
    else:
        assert all(checks)

def test_iter_raw(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")
    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            assert not response.internal_response._content_consumed
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += part
        assert raw == b"Hello, world!"
    assert response.internal_response._content_consumed
    assert response.is_closed
    assert response.is_stream_consumed

def test_iter_raw_on_iterable(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/iterable")

    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

def test_iter_with_error(client):
    request = HttpRequest("GET", "http://localhost:5000/errors/403")

    with client.send_request(request, stream=True) as response:
        with pytest.raises(HttpResponseError):
            response.raise_for_status()
    assert response.is_closed

    with pytest.raises(HttpResponseError):
        with client.send_request(request, stream=True) as response:
            response.raise_for_status()
    assert response.is_closed

    request = HttpRequest("GET", "http://doesNotExist")
    with pytest.raises(ServiceRequestError):
        with client.send_request(request, stream=True) as response:
            raise ValueError("Should error before entering")
    assert response.is_closed

def test_iter_raw_with_chunksize(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_raw(chunk_size=5)]
        assert parts == [b"Hello", b", wor", b"ld!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_raw(chunk_size=13)]
        assert parts == [b"Hello, world!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_raw(chunk_size=20)]
        assert parts == [b"Hello, world!"]

def test_iter_raw_num_bytes_downloaded(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        num_downloaded = response.num_bytes_downloaded
        for part in response.iter_raw():
            assert len(part) == (response.num_bytes_downloaded - num_downloaded)
            num_downloaded = response.num_bytes_downloaded

def test_iter_bytes(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        raw = b""
        for chunk in response.iter_bytes():
            assert not response.internal_response._content_consumed
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += chunk
        assert response.internal_response._content_consumed
        assert response.is_closed
        assert response.is_stream_consumed
        assert raw == b"Hello, world!"

def test_iter_bytes_with_chunk_size(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_bytes(chunk_size=5)]
        assert parts == [b"Hello", b", wor", b"ld!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_bytes(chunk_size=13)]
        assert parts == [b"Hello, world!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_bytes(chunk_size=20)]
        assert parts == [b"Hello, world!"]

def test_iter_text(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/string")

    with client.send_request(request, stream=True) as response:
        content = ""
        for part in response.iter_text():
            content += part
        assert content == "Hello, world!"

def test_iter_text_with_chunk_size(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/string")

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_text(chunk_size=5)]
        assert parts == ["Hello", ", wor", "ld!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_text(chunk_size=13)]
        assert parts == ["Hello, world!"]

    with client.send_request(request, stream=True) as response:
        parts = [part for part in response.iter_text(chunk_size=20)]
        assert parts == ["Hello, world!"]

def test_iter_lines(client):
    request = HttpRequest("GET", "http://localhost:5000/basic/lines")

    with client.send_request(request, stream=True) as response:
        content = []
        for line in response.iter_lines():
            content.append(line)
        assert content == ["Hello,\n", "world!"]

def test_sync_streaming_response(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = response.read()

        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed

def test_cannot_read_after_stream_consumed(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        content = b""
        for part in response.iter_bytes():
            content += part

        assert content == b"Hello, world!"

        with pytest.raises(StreamConsumedError) as ex:
            response.read()

    assert "You are attempting to read or stream content that has already been streamed." in str(ex.value)

def test_cannot_read_after_response_closed(client):
    request = HttpRequest("GET", "http://localhost:5000/streams/basic")

    with client.send_request(request, stream=True) as response:
        response.close()
        with pytest.raises(ResponseClosedError) as ex:
            response.read()
    assert "You can not try to read or stream this response's content, since the response has been closed" in str(ex.value)
