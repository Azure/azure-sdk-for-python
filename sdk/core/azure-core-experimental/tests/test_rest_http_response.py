# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import io
import pytest
from itertools import product

from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest as RestHttpRequest
import xml.etree.ElementTree as ET

from rest_client import MockRestClient
from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, create_http_request


@pytest.fixture
def send_request():
    def _send_request(port, request, transport):
        client = MockRestClient(port, transport=transport)
        response = client.send_request(request, stream=False)
        response.raise_for_status()
        return response

    return _send_request


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/string")
    response = send_request(port, request, transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:{}/basic/string".format(port)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_content(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/bytes")
    response = send_request(port, request, transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_text(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/string")
    response = send_request(port, request, transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"
    assert response.headers["Content-Length"] == "13"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert response.content_type == "text/plain; charset=utf-8"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_html(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/html")
    response = send_request(port, request, transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "<html><body>Hello, world!</html></body>"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_raise_for_status(port, transport, requesttype):
    client = MockRestClient(port, transport=transport())
    request = create_http_request(requesttype, "GET", "/basic/string")
    response = client.send_request(request)
    response.raise_for_status()

    request = create_http_request(requesttype, "GET", "/errors/403")
    response = client.send_request(request)
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    request = create_http_request(requesttype, "GET", "/errors/500")
    response = client.send_request(
        request,
        retry_total=0,  # takes too long with retires on 500
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_repr(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/string")
    response = send_request(port, request, transport())
    assert repr(response) == "<HttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_content_type_encoding(send_request, port, transport, requesttype):
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    request = create_http_request(requesttype, "GET", "/encoding/latin-1")
    response = send_request(port, request, transport())
    assert response.content_type == "text/plain; charset=latin-1"
    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_autodetect_encoding(send_request, port, transport, requesttype):
    """
    Autodetect encoding if there is no Content-Type header.
    """
    request = create_http_request(requesttype, "GET", "/encoding/latin-1")
    response = send_request(port, request, transport())

    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_fallback_to_autodetect(send_request, port, transport, requesttype):
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    request = create_http_request(requesttype, "GET", "/encoding/invalid-codec-name")
    response = send_request(port, request, transport())

    assert response.headers["Content-Type"] == "text/plain; charset=invalid-codec-name"
    assert response.text() == "おはようございます。"
    assert response.encoding is None


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_no_charset_with_ascii_content(send_request, port, transport, requesttype):
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    request = create_http_request(requesttype, "GET", "/encoding/no-charset")
    response = send_request(port, request, transport())
    assert response.headers["Content-Type"] == "text/plain"
    assert response.status_code == 200
    assert response.encoding is None
    assert response.text() == "Hello, world!"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_response_no_charset_with_iso_8859_1_content(send_request, port, transport, requesttype):
    """
    We don't support iso-8859-1 by default following conversations
    about encoding flow
    """
    request = create_http_request(requesttype, "GET", "/encoding/iso-8859-1")
    response = send_request(port, request, transport())
    assert response.text() == "Accented: �sterreich"
    assert response.encoding is None


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_json(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/basic/json")
    response = send_request(port, request, transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding is None


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_json_with_specified_encoding(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/json")
    response = send_request(port, request, transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_emoji(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/emoji")
    response = send_request(port, request, transport())
    assert response.text() == "👩"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_emoji_family_with_skin_tone_modifier(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/emoji-family-skin-tone-modifier")
    response = send_request(port, request, transport())
    assert response.text() == "👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_korean_nfc(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/korean")
    response = send_request(port, request, transport())
    assert response.text() == "아가"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_urlencoded_content(send_request, port, transport, requesttype):
    request = create_http_request(
        requesttype,
        "POST",
        "/urlencoded/pet/add/1",
        data={"pet_type": "dog", "pet_food": "meat", "name": "Fido", "pet_age": 42},
    )
    send_request(port, request, transport())


# This format of file data is not compatible with legacy HttpRequest object, as the files
# structure is not compatible with the retry policy.
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_files_content(send_request, port, transport):
    request = create_http_request(
        RestHttpRequest,
        "POST",
        "/multipart/basic",
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    send_request(port, request, transport())


# This format of file data is not compatible with legacy HttpRequest object, as the files
# structure is not compatible with the retry policy.
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_data_and_files_content(send_request, port, transport):
    request = create_http_request(
        RestHttpRequest,
        "POST",
        "/multipart/data-and-files",
        data={"message": "Hello, world!"},
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    send_request(port, request, transport())


# This format of file data is not compatible with legacy HttpRequest object, as the files
# structure is not compatible with the retry policy.
@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_encode_non_seekable_filelike(send_request, port, transport):
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
    request = create_http_request(
        RestHttpRequest,
        "POST",
        "/multipart/non-seekable-filelike",
        files=files,
    )
    send_request(port, request, transport())


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_get_xml_basic(send_request, port, transport, requesttype):
    request = create_http_request(
        requesttype,
        "GET",
        "/xml/basic",
    )
    response = send_request(port, request, transport())
    parsed_xml = ET.fromstring(response.text())
    assert parsed_xml.tag == "slideshow"
    attributes = parsed_xml.attrib
    assert attributes["title"] == "Sample Slide Show"
    assert attributes["date"] == "Date of publication"
    assert attributes["author"] == "Yours Truly"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_put_xml_basic(send_request, port, transport, requesttype):

    basic_body = """<?xml version='1.0' encoding='UTF-8'?>
<slideshow
        title="Sample Slide Show"
        date="Date of publication"
        author="Yours Truly">
    <slide type="all">
        <title>Wake up to WonderWidgets!</title>
    </slide>
    <slide type="all">
        <title>Overview</title>
        <item>Why WonderWidgets are great</item>
        <item></item>
        <item>Who buys WonderWidgets</item>
    </slide>
</slideshow>"""

    request = create_http_request(
        requesttype,
        "PUT",
        "/xml/basic",
        content=ET.fromstring(basic_body),
    )
    send_request(port, request, transport())


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_text_and_encoding(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/emoji")
    response = send_request(port, request, transport())
    assert response.content == "👩".encode("utf-8")
    assert response.text() == "👩"

    # try setting encoding as a property
    response.encoding = "utf-16"
    assert response.text() == "鿰ꦑ" == response.content.decode(response.encoding)

    # assert latin-1 changes text decoding without changing encoding property
    assert response.text("latin-1") == "ð\x9f\x91©" == response.content.decode("latin-1")
    assert response.encoding == "utf-16"


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_passing_encoding_to_text(send_request, port, transport, requesttype):
    request = create_http_request(requesttype, "GET", "/encoding/emoji")
    response = send_request(port, request, transport())
    assert response.content == "👩".encode("utf-8")
    assert response.text() == "👩"

    # pass in different encoding
    assert response.text("latin-1") == "ð\x9f\x91©"

    # check response.text() still gets us the old value
    assert response.text() == "👩"
