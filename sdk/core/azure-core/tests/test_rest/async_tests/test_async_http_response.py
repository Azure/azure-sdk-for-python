# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import functools
import pytest
import aiohttp
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.exceptions import HttpResponseError
from typing import Any, Dict

@pytest.fixture
def send_request(client):
    async def _send_request(request):
        return await client.send_request(request, stream=False)
    return _send_request

@pytest.mark.asyncio
async def test_response(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/string"),
    )

    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:3000/basic/helloWorld/string"
    response.raise_for_status()


@pytest.mark.asyncio
async def test_response_content(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/bytes"),
    )

    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"
    response.raise_for_status()


@pytest.mark.asyncio
async def test_response_text(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text"),
    )

    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"
    assert response.headers["Content-Length"] == '13'
    assert response.headers['Content-Type'] == "text/plain; charset=utf-8"
    response.raise_for_status()


@pytest.mark.asyncio
async def test_response_html(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/html"),
    )

    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"<html><body>Hello, world!</html></body>"
    assert response.text == "<html><body>Hello, world!</html></body>"
    response.raise_for_status()

@pytest.mark.asyncio
async def test_raise_for_status(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text"),
    )
    response.raise_for_status()

    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/errors/403"),
    )
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/errors/500"),
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

@pytest.mark.asyncio
async def test_response_repr(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text")
    )
    assert repr(response) == "<AsyncHttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"

@pytest.mark.asyncio
async def test_response_content_type_encoding(send_request):
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    await response.read()
    assert response.content == b'Latin 1: \xff'
    assert response.text == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.asyncio
async def test_response_autodetect_encoding(send_request):
    """
    Autodetect encoding if there is no Content-Type header.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    await response.read()

    # going to hack no content type response header being sent back
    response._internal_response.headers["Content-Type"] = ""
    assert response.text == u'Latin 1: ÿ'
    assert response.encoding is None


@pytest.mark.asyncio
async def test_response_fallback_to_autodetect(send_request):
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    await response.read()

    # can't actually send incorrect charset from testserver, so overriding to bad charset
    response._internal_response.headers["Content-Type"] = "text-plain; charset=invalid-codec-name"
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding is None


@pytest.mark.asyncio
async def test_response_no_charset_with_ascii_content(send_request):
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/string"),
    )

    # charset's will get added in real calls to testserver, so just changing content
    # type to remove charset
    response._internal_response.headers["Content-Type"] = "text/plain"
    assert response.status_code == 200
    assert response.encoding is None
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"


@pytest.mark.asyncio
async def test_response_no_charset_with_iso_8859_1_content(send_request):
    """
    A response with ISO 8859-1 encoded content should decode correctly,
    even with no charset specified.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/iso-8859-1"),
    )
    content = await response.read()
     # charset's will get added in real calls to testserver, so just changing content
    # type to remove charset
    response._internal_response.headers["Content-Type"] = "text/plain"
    assert content == b'Accented: \xc3\x96sterreich'
    assert response.text == "Accented: Österreich"
    assert response.encoding is None

@pytest.mark.asyncio
async def test_response_set_explicit_encoding(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1-string-with-utf-8"),
    )
    response.encoding = "latin-1"
    content = await response.read()
    assert content == b'Latin 1: \xff'
    assert response.text == "Latin 1: ÿ"
    assert response.encoding == "latin-1"

@pytest.mark.asyncio
async def test_json(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/basic/json"),
    )
    await response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}

@pytest.mark.asyncio
async def test_json_with_specified_encoding(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/json"),
    )
    await response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"

@pytest.mark.asyncio
async def test_emoji(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/emoji"),
    )
    await response.read()
    assert response.text == "👩"

@pytest.mark.asyncio
async def test_emoji_family_with_skin_tone_modifier(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/emoji-family-skin-tone-modifier"),
    )
    await response.read()
    assert response.text == "👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"

@pytest.mark.asyncio
async def test_korean_nfc(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:3000/encoding/korean"),
    )
    await response.read()
    assert response.text == "아가"
