# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import pytest
from azure.core.rest import HttpRequest
import collections.abc

@pytest.fixture
def assert_aiterator_body():
    async def _comparer(request, final_value):
        parts = []
        async for part in request.content:
            parts.append(part)
        content = b"".join(parts)
        assert content == final_value
    return _comparer

def test_transfer_encoding_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")

    request = HttpRequest("POST", "http://example.org", data=data)
    assert "Content-Length" not in request.headers

def test_override_content_length_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")
    headers = {"Content-Length": "0"}

    request = HttpRequest("POST", "http://example.org", data=data, headers=headers)
    assert request.headers["Content-Length"] == "0"

@pytest.mark.asyncio
async def test_aiterbale_content(assert_aiterator_body):
    class Content:
        async def __aiter__(self):
            yield b"test 123"

    request = HttpRequest("POST", "http://example.org", content=Content())
    assert request.headers == {}
    await assert_aiterator_body(request, b"test 123")

@pytest.mark.asyncio
async def test_aiterator_content(assert_aiterator_body):
    async def hello_world():
        yield b"Hello, "
        yield b"world!"

    request = HttpRequest("POST", url="http://example.org", content=hello_world())
    assert not isinstance(request._data, collections.abc.Iterable)
    assert isinstance(request._data, collections.abc.AsyncIterable)

    assert request.headers == {}
    await assert_aiterator_body(request, b"Hello, world!")

    # Support 'data' for compat with requests.
    request = HttpRequest("POST", url="http://example.org", data=hello_world())
    assert not isinstance(request._data, collections.abc.Iterable)
    assert isinstance(request._data, collections.abc.AsyncIterable)

    assert request.headers == {}
    await assert_aiterator_body(request, b"Hello, world!")

    # transfer encoding should not be set for GET requests
    request = HttpRequest("GET", url="http://example.org", data=hello_world())
    assert not isinstance(request._data, collections.abc.Iterable)
    assert isinstance(request._data, collections.abc.AsyncIterable)

    assert request.headers == {}
    await assert_aiterator_body(request, b"Hello, world!")

@pytest.mark.asyncio
async def test_read_content(assert_aiterator_body):
    async def content():
        yield b"test 123"

    request = HttpRequest("POST", "http://example.org", content=content())
    await assert_aiterator_body(request, b"test 123")
    # in this case, request._data is what we end up passing to the requests transport
    assert isinstance(request._data, collections.abc.AsyncIterable)
