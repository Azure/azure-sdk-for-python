# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import io
import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import HttpResponseError

@pytest.fixture
def send_request(client):
    async def _send_request(request):
        response = await client.send_request(request, stream=False)
        response.raise_for_status()
        return response
    return _send_request

@pytest.mark.asyncio
async def test_response(send_request):
    response = await send_request(
        HttpRequest("GET", "http://localhost:5000/basic/string"),
    )
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.content == b"Hello, world!"
    assert response.text == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:5000/basic/string"

@pytest.mark.asyncio
async def test_response_content(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/basic/bytes"),
    )
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"

@pytest.mark.asyncio
async def test_response_text(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/basic/string"),
    )
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text == "Hello, world!"
    assert response.headers["Content-Length"] == '13'
    assert response.headers['Content-Type'] == "text/plain; charset=utf-8"

@pytest.mark.asyncio
async def test_response_html(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/basic/html"),
    )
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"<html><body>Hello, world!</html></body>"
    assert response.text == "<html><body>Hello, world!</html></body>"

@pytest.mark.asyncio
async def test_raise_for_status(client):
    # response = await client.send_request(
    #     HttpRequest("GET", "http://localhost:5000/basic/string"),
    # )
    # response.raise_for_status()

    response = await client.send_request(
        HttpRequest("GET", "http://localhost:5000/errors/403"),
    )
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = await client.send_request(
        HttpRequest("GET", "http://localhost:5000/errors/500"),
        retry_total=0,  # takes too long with retires on 500
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

@pytest.mark.asyncio
async def test_response_repr(send_request):
    response = await send_request(
        HttpRequest("GET", "http://localhost:5000/basic/string")
    )
    assert repr(response) == "<AsyncHttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"

@pytest.mark.asyncio
async def test_response_content_type_encoding(send_request):
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/latin-1")
    )
    await response.read()
    assert response.content_type == "text/plain; charset=latin-1"
    assert response.content == b'Latin 1: \xff'
    assert response.text == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.asyncio
async def test_response_autodetect_encoding(send_request):
    """
    Autodetect encoding if there is no Content-Type header.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/latin-1")
    )
    await response.read()
    assert response.text == u'Latin 1: ÿ'
    assert response.encoding == "latin-1"


@pytest.mark.asyncio
async def test_response_fallback_to_autodetect(send_request):
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/invalid-codec-name")
    )
    await response.read()
    assert response.headers["Content-Type"] == "text/plain; charset=invalid-codec-name"
    assert response.text == "おはようございます。"
    assert response.encoding is None


@pytest.mark.asyncio
async def test_response_no_charset_with_ascii_content(send_request):
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/no-charset"),
    )

    assert response.headers["Content-Type"] == "text/plain"
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
        request=HttpRequest("GET", "http://localhost:5000/encoding/iso-8859-1"),
    )
    await response.read()
    assert response.text == u"Accented: Österreich"
    assert response.encoding is None

# NOTE: aiohttp isn't liking this
# @pytest.mark.asyncio
# async def test_response_set_explicit_encoding(send_request):
#     response = await send_request(
#         request=HttpRequest("GET", "http://localhost:5000/encoding/latin-1-with-utf-8"),
#     )
#     assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
#     response.encoding = "latin-1"
#     await response.read()
#     assert response.text == "Latin 1: ÿ"
#     assert response.encoding == "latin-1"

@pytest.mark.asyncio
async def test_json(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/basic/json"),
    )
    await response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding is None

@pytest.mark.asyncio
async def test_json_with_specified_encoding(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/json"),
    )
    await response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"

@pytest.mark.asyncio
async def test_emoji(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/emoji"),
    )
    await response.read()
    assert response.text == "👩"

@pytest.mark.asyncio
async def test_emoji_family_with_skin_tone_modifier(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/emoji-family-skin-tone-modifier"),
    )
    await response.read()
    assert response.text == "👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"

@pytest.mark.asyncio
async def test_korean_nfc(send_request):
    response = await send_request(
        request=HttpRequest("GET", "http://localhost:5000/encoding/korean"),
    )
    await response.read()
    assert response.text == "아가"

@pytest.mark.asyncio
async def test_urlencoded_content(send_request):
    await send_request(
        request=HttpRequest(
            "POST",
            "http://localhost:5000/urlencoded/pet/add/1",
            data={ "pet_type": "dog", "pet_food": "meat", "name": "Fido", "pet_age": 42 }
        ),
    )

@pytest.mark.asyncio
async def test_multipart_files_content(send_request):
    request = HttpRequest(
        "POST",
        "http://localhost:5000/multipart/basic",
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    await send_request(request)

@pytest.mark.asyncio
async def test_multipart_encode_non_seekable_filelike(send_request):
    """
    Test that special readable but non-seekable filelike objects are supported,
    at the cost of reading them into memory at most once.
    """

    class IteratorIO(io.IOBase):
        def __init__(self, iterator):
            self._iterator = iterator

        def read(self, *args):
            return b"".join(self._iterator)

    def data():
        yield b"Hello"
        yield b"World"

    fileobj = IteratorIO(data())
    files = {"file": fileobj}
    request = HttpRequest(
        "POST",
        "http://localhost:5000/multipart/non-seekable-filelike",
        files=files,
    )
    await send_request(request)
