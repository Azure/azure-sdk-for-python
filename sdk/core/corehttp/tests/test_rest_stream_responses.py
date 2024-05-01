# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.rest import HttpRequest
from corehttp.exceptions import StreamClosedError, StreamConsumedError, ResponseNotReadError
from corehttp.exceptions import HttpResponseError, ServiceRequestError

from rest_client import MockRestClient
from utils import SYNC_TRANSPORTS


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_raw(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += part
        assert raw == b"Hello, world!"
    assert response.is_closed
    assert response.is_stream_consumed


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_raw_on_iterable(port, transport):
    request = HttpRequest("GET", "/streams/iterable")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        raw = b""
        for part in response.iter_raw():
            raw += part
        assert raw == b"Hello, world!"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_with_error(port, transport):
    request = HttpRequest("GET", "/errors/403")
    client = MockRestClient(port, transport=transport())
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


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_bytes(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        raw = b""
        for chunk in response.iter_bytes():
            assert not response.is_closed
            assert response.is_stream_consumed  # we follow httpx behavior here
            raw += chunk
        assert response.is_closed
        assert response.is_stream_consumed
        assert raw == b"Hello, world!"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_sync_streaming_response(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        assert response.status_code == 200
        assert not response.is_closed

        content = response.read()

        assert content == b"Hello, world!"
        assert response.content == b"Hello, world!"
        assert response.is_closed


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_cannot_read_after_stream_consumed(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        content = b""
        for part in response.iter_bytes():
            content += part

        assert content == b"Hello, world!"

        with pytest.raises(StreamConsumedError) as ex:
            response.read()

    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "You have likely already consumed this stream, so it can not be accessed anymore" in str(ex.value)


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_cannot_read_after_response_closed(port, transport):
    request = HttpRequest("GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        response.close()
        with pytest.raises(StreamClosedError) as ex:
            response.read()
    # breaking up assert into multiple lines
    assert "<HttpRequest [GET], url: 'http://localhost:{}/streams/basic'>".format(port) in str(ex.value)
    assert "can no longer be read or streamed, since the response has already been closed" in str(ex.value)


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_read(port, transport):
    # thanks to McCoy Patiño for this test!
    request = HttpRequest("GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=True)
    response.read()
    iterator = response.iter_bytes()
    for part in iterator:
        assert part
    assert response.text()


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_iter_read_back_and_forth(port, transport):
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
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


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_error_reading(port, transport):
    request = HttpRequest("GET", "/errors/403")
    client = MockRestClient(port, transport=transport())
    with client.send_request(request, stream=True) as response:
        response.read()
        assert response.content == b""

    response = client.send_request(request, stream=True)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()
    response.read()
    assert response.content == b""
    # try giving a really slow response, see what happens


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_pass_kwarg_to_iter_bytes(port, transport):
    request = HttpRequest("GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=True)
    for part in response.iter_bytes(chunk_size=5):
        assert part


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_pass_kwarg_to_iter_raw(port, transport):
    request = HttpRequest("GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=True)
    for part in response.iter_raw(chunk_size=5):
        assert part


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_header(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request)
    content = response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_deflate_decompress_compressed_header(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/deflate")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request)
    content = response.read()
    assert content == b"hi there"
    assert response.content == content
    assert response.text() == "hi there"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_decompress_compressed_header_stream(port, transport):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=True)
    content = response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"
