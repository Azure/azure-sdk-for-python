# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import StreamClosedError, StreamConsumedError, ResponseNotReadError
from azure.core.exceptions import HttpResponseError, ServiceRequestError

def _assert_stream_state(response, open):
    # if open is true, check the stream is open.
    # if false, check if everything is closed
    checks = [
        response._internal_response._content_consumed,
        response.is_closed,
        response.is_stream_consumed
    ]
    if open:
        assert not any(checks)
    else:
        assert all(checks)

def test_iter_raw(client):
    request = HttpRequest("GET", "/streams/basic")
    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            assert not response._internal_response._content_consumed
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += part
        assert raw == b"Hello, world!"
    assert response._internal_response._content_consumed
    assert response.is_closed
    assert response.is_stream_consumed

def test_iter_raw_on_iterable(client):
    request = HttpRequest("GET", "/streams/iterable")

    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"

def test_iter_with_error(client):
    request = HttpRequest("GET", "/errors/403")

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

def test_iter_bytes(client):
    request = HttpRequest("GET", "/streams/basic")

    with client.send_request(request, stream=True) as response:
        raw = b""
        for chunk in response.iter_bytes():
            assert not response._internal_response._content_consumed
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += chunk
        assert response._internal_response._content_consumed
        assert response.is_closed
        assert response.is_stream_consumed
        assert raw == b"Hello, world!"

@pytest.mark.skip(reason="We've gotten rid of iter_text for now")
def test_iter_text(client):
    request = HttpRequest("GET", "/basic/string")
    with client.send_request(request, stream=True) as response:
        content = ""
        for part in response.iter_text():
            content += part
        assert content == "Hello, world!"

@pytest.mark.skip(reason="We've gotten rid of iter_lines for now")
def test_iter_lines(client):
    request = HttpRequest("GET", "/basic/lines")

    with client.send_request(request, stream=True) as response:
        content = []
        for line in response.iter_lines():
            content.append(line)
        assert content == ["Hello,\n", "world!"]

def test_sync_streaming_response(client):
    request = HttpRequest("GET", "/streams/basic")

    with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = response.read()

        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed

def test_cannot_read_after_stream_consumed(client, port):
    request = HttpRequest("GET", "/streams/basic")

    with client.send_request(request, stream=True) as response:
        content = b""
        for part in response.iter_bytes():
            content += part

        assert content == b"Hello, world!"

        with pytest.raises(StreamConsumedError) as ex:
            response.read()

    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "You have likely already consumed this stream, so it can not be accessed anymore" in str(ex.value)

def test_cannot_read_after_response_closed(port, client):
    request = HttpRequest("GET", "/streams/basic")

    with client.send_request(request, stream=True) as response:
        response.close()
        with pytest.raises(StreamClosedError) as ex:
            response.read()
    # breaking up assert into multiple lines
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "can no longer be read or streamed, since the response has already been closed" in str(ex.value)

def test_decompress_plain_no_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    response = client.send_request(request, stream=True)
    with pytest.raises(ResponseNotReadError):
        response.content
    response.read()
    assert response.content == b"test"

def test_compress_plain_no_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.txt".format(account_name)
    request = HttpRequest("GET", url)
    response = client.send_request(request, stream=True)
    iter = response.iter_raw()
    data = b"".join(list(iter))
    assert data == b"test"

def test_decompress_compressed_no_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    url = "https://{}.blob.core.windows.net/tests/test.tar.gz".format(account_name)
    request = HttpRequest("GET", url)
    response = client.send_request(request, stream=True)
    iter = response.iter_bytes()
    data = b"".join(list(iter))
    assert data == b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\n+I-.\x01\x00\x0c~\x7f\xd8\x04\x00\x00\x00'

def test_decompress_compressed_header(client):
    # thanks to Xiang Yan for this test!
    account_name = "coretests"
    account_url = "https://{}.blob.core.windows.net".format(account_name)
    url = "https://{}.blob.core.windows.net/tests/test_with_header.tar.gz".format(account_name)
    request = HttpRequest("GET", url)
    response = client.send_request(request, stream=True)
    iter = response.iter_bytes()
    data = b"".join(list(iter))
    assert data == b"test"

def test_iter_read(client):
    # thanks to McCoy Patiño for this test!
    request = HttpRequest("GET", "/basic/string")
    response = client.send_request(request, stream=True)
    response.read()
    iterator = response.iter_bytes()
    for part in iterator:
        assert part
    assert response.text()

def test_iter_read_back_and_forth(client):
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "/basic/string")
    response = client.send_request(request, stream=True)
    iterator = response.iter_bytes()
    for part in iterator:
        assert part
    with pytest.raises(ResponseNotReadError):
        response.text()
    with pytest.raises(StreamConsumedError):
        response.read()
    with pytest.raises(ResponseNotReadError):
        response.text()

def test_stream_with_return_pipeline_response(client):
    request = HttpRequest("GET", "/basic/string")
    pipeline_response = client.send_request(request, stream=True, _return_pipeline_response=True)
    assert hasattr(pipeline_response, "http_request")
    assert hasattr(pipeline_response, "http_response")
    assert hasattr(pipeline_response, "context")
    assert list(pipeline_response.http_response.iter_bytes()) == [b'Hello, world!']

def test_error_reading(client):
    request = HttpRequest("GET", "/errors/403")
    with client.send_request(request, stream=True) as response:
        response.read()
        assert response.content == b""

    response = client.send_request(request, stream=True)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()
    response.read()
    assert response.content == b""
    # try giving a really slow response, see what happens

def test_pass_kwarg_to_iter_bytes(client):
    request = HttpRequest("GET", "/basic/string")
    response = client.send_request(request, stream=True)
    for part in response.iter_bytes(chunk_size=5):
        assert part

def test_pass_kwarg_to_iter_raw(client):
    request = HttpRequest("GET", "/basic/string")
    response = client.send_request(request, stream=True)
    for part in response.iter_raw(chunk_size=5):
        assert part

def test_decompress_compressed_header(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = client.send_request(request)
    content = response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

def test_decompress_compressed_header_stream(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = client.send_request(request, stream=True)
    content = response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

def test_decompress_compressed_header_stream_body_content(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = client.send_request(request, stream=True)
    response.read()
    content = response.content
    assert content == response.body()
