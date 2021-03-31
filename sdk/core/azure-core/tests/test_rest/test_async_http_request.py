# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import pytest
from azure.core.rest import HttpRequest
from typing import AsyncGenerator

def test_rest_transfer_encoding_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")

    request = HttpRequest("POST", "http://example.org", data=data)
    assert "Content-Length" not in request.headers
    assert request.headers["Transfer-Encoding"] == "chunked"

def test_rest_override_content_length_header():
    async def streaming_body(data):
        yield data  # pragma: nocover

    data = streaming_body(b"test 123")
    headers = {"Content-Length": "0"}

    request = HttpRequest("POST", "http://example.org", data=data, headers=headers)
    assert request.headers["Content-Length"] == "0"

@pytest.mark.asyncio
async def test_rest_aiterator_content():
    async def hello_world():
        yield b"Hello, "
        yield b"world!"

    request = HttpRequest("POST", url="http://example.org", content=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked", "Content-Type": "application/octet-stream"}
    assert isinstance(request.content, AsyncGenerator)

    # Support 'data' for compat with requests.
    request = HttpRequest("POST", url="http://example.org", data=hello_world())

    assert request.headers == {"Transfer-Encoding": "chunked", "Content-Type": "application/octet-stream"}
    assert isinstance(request.content, AsyncGenerator)

    # transfer encoding should not be set for GET requests
    request = HttpRequest("GET", url="http://example.org", data=hello_world())

    assert request.headers == {"Content-Type": "application/octet-stream"}
    assert isinstance(request.content, AsyncGenerator)

