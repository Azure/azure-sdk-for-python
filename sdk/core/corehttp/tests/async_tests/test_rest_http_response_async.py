# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import io
import pytest

from corehttp.rest import HttpRequest, AsyncHttpResponse
from corehttp.exceptions import HttpResponseError
from utils import ASYNC_TRANSPORTS, readonly_checks

from rest_client_async import AsyncMockRestClient


@pytest.fixture
def send_request(port):
    async def _send_request(request, transport):
        client = AsyncMockRestClient(port, transport=transport)
        async with client:
            response = await client.send_request(request, stream=False)
            response.raise_for_status()
            return response

    return _send_request


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response(send_request, port, transport):
    response = await send_request(HttpRequest("GET", "/basic/string"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.content == b"Hello, world!"
    assert response.text() == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:{}/basic/string".format(port)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_content(send_request, transport):
    response = await send_request(HttpRequest("GET", "/basic/bytes"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text() == "Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_text(send_request, transport):
    response = await send_request(HttpRequest("GET", "/basic/string"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text() == "Hello, world!"
    assert response.headers["Content-Length"] == "13"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_html(send_request, transport):
    response = await send_request(HttpRequest("GET", "/basic/html"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    content = await response.read()
    assert content == b"<html><body>Hello, world!</html></body>"
    assert response.text() == "<html><body>Hello, world!</html></body>"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_raise_for_status(port, transport):
    client = AsyncMockRestClient(port, transport=transport())
    response = await client.send_request(HttpRequest("GET", "/errors/403"))
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = await client.send_request(
        HttpRequest("GET", "/errors/500"),
        retry_total=0,  # takes too long with retires on 500
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_repr(send_request, transport):
    response = await send_request(HttpRequest("GET", "/basic/string"), transport())
    assert repr(response) == "<AsyncHttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_content_type_encoding(send_request, transport):
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    response = await send_request(HttpRequest("GET", "/encoding/latin-1"), transport())
    assert response.content_type == "text/plain; charset=latin-1"
    assert response.content == b"Latin 1: \xff"
    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_autodetect_encoding(send_request, transport):
    """
    Autodetect encoding if there is no Content-Type header.
    """
    response = await send_request(HttpRequest("GET", "/encoding/latin-1"), transport())
    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_fallback_to_autodetect(send_request, transport):
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    response = await send_request(HttpRequest("GET", "/encoding/invalid-codec-name"), transport())
    assert response.headers["Content-Type"] == "text/plain; charset=invalid-codec-name"
    assert response.text() == "おはようございます。"
    assert response.encoding is None


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_no_charset_with_ascii_content(send_request, transport):
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    response = await send_request(HttpRequest("GET", "/encoding/no-charset"), transport())

    assert response.headers["Content-Type"] == "text/plain"
    assert response.status_code == 200
    assert response.encoding is None
    content = await response.read()
    assert content == b"Hello, world!"
    assert response.text() == "Hello, world!"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_response_no_charset_with_iso_8859_1_content(send_request, transport):
    """
    We don't support iso-8859-1 by default following conversations
    about encoding flow
    """
    response = await send_request(HttpRequest("GET", "/encoding/iso-8859-1"), transport())
    assert response.text() == "Accented: �sterreich"
    assert response.encoding is None


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_json(send_request, transport):
    response = await send_request(HttpRequest("GET", "/basic/json"), transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding is None


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_json_with_specified_encoding(send_request, transport):
    response = await send_request(HttpRequest("GET", "/encoding/json"), transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_emoji(send_request, transport):
    response = await send_request(HttpRequest("GET", "/encoding/emoji"), transport())
    assert response.text() == "👩"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_emoji_family_with_skin_tone_modifier(send_request, transport):
    response = await send_request(HttpRequest("GET", "/encoding/emoji-family-skin-tone-modifier"), transport())
    assert response.text() == "👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_korean_nfc(send_request, transport):
    response = await send_request(HttpRequest("GET", "/encoding/korean"), transport())
    assert response.text() == "아가"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_urlencoded_content(send_request, transport):
    await send_request(
        HttpRequest(
            "POST", "/urlencoded/pet/add/1", data={"pet_type": "dog", "pet_food": "meat", "name": "Fido", "pet_age": 42}
        ),
        transport(),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_multipart_files_content(send_request, transport):
    request = HttpRequest(
        "POST",
        "/multipart/basic",
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    await send_request(request, transport())


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_multipart_data_and_files_content(send_request, transport):
    request = HttpRequest(
        "POST",
        "/multipart/data-and-files",
        data={"message": "Hello, world!"},
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    await send_request(request, transport())


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_text_and_encoding(send_request, transport):
    response = await send_request(HttpRequest("GET", "/encoding/emoji"), transport())
    assert response.content == "👩".encode("utf-8")
    assert response.text() == "👩"

    # try setting encoding as a property
    response.encoding = "utf-16"
    assert response.text() == "鿰ꦑ" == response.content.decode(response.encoding)

    # assert latin-1 changes text decoding without changing encoding property
    assert response.text("latin-1") == "ð\x9f\x91©" == response.content.decode("latin-1")
    assert response.encoding == "utf-16"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_multipart_encode_non_seekable_filelike(send_request, transport):
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
        "/multipart/non-seekable-filelike",
        files=files,
    )
    await send_request(request, transport())


def test_initialize_response_abc():
    with pytest.raises(TypeError) as ex:
        AsyncHttpResponse()
    assert "Can't instantiate abstract class" in str(ex)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_readonly(send_request, transport):
    """Make sure everything that is readonly is readonly"""
    response = await send_request(HttpRequest("GET", "/health"), transport())
    readonly_checks(response)
