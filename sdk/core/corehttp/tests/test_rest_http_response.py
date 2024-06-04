# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import io
import pytest
from corehttp.rest import HttpRequest, HttpResponse
from corehttp.rest._requests_basic import RestRequestsTransportResponse
from corehttp.exceptions import HttpResponseError
import xml.etree.ElementTree as ET

from rest_client import MockRestClient
from utils import readonly_checks, SYNC_TRANSPORTS


@pytest.fixture
def send_request(port):
    def _send_request(request, transport):
        client = MockRestClient(port, transport=transport)
        response = client.send_request(request, stream=False)
        response.raise_for_status()
        return response

    return _send_request


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response(send_request, port, transport):
    response = send_request(HttpRequest("GET", "/basic/string"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:{}/basic/string".format(port)


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_content(send_request, transport):
    response = send_request(HttpRequest("GET", "/basic/bytes"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_text(send_request, transport):
    response = send_request(HttpRequest("GET", "/basic/string"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "Hello, world!"
    assert response.headers["Content-Length"] == "13"
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert response.content_type == "text/plain; charset=utf-8"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_html(send_request, transport):
    response = send_request(HttpRequest("GET", "/basic/html"), transport())
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text() == "<html><body>Hello, world!</html></body>"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_raise_for_status(port, transport):
    client = MockRestClient(port, transport=transport())
    response = client.send_request(HttpRequest("GET", "/basic/string"))
    response.raise_for_status()

    response = client.send_request(
        HttpRequest("GET", "/errors/403"),
    )
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = client.send_request(
        HttpRequest("GET", "/errors/500"),
        retry_total=0,  # takes too long with retires on 500
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_repr(send_request, transport):
    response = send_request(HttpRequest("GET", "/basic/string"), transport())
    assert repr(response) == "<HttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_content_type_encoding(send_request, transport):
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    response = send_request(HttpRequest("GET", "/encoding/latin-1"), transport())
    assert response.content_type == "text/plain; charset=latin-1"
    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_autodetect_encoding(send_request, transport):
    """
    Autodetect encoding if there is no Content-Type header.
    """
    response = send_request(HttpRequest("GET", "/encoding/latin-1"), transport())

    assert response.text() == "Latin 1: ÿ"
    assert response.encoding == "latin-1"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_fallback_to_autodetect(send_request, transport):
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    response = send_request(HttpRequest("GET", "/encoding/invalid-codec-name"), transport())

    assert response.headers["Content-Type"] == "text/plain; charset=invalid-codec-name"
    assert response.text() == "おはようございます。"
    assert response.encoding is None


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_no_charset_with_ascii_content(send_request, transport):
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    response = send_request(HttpRequest("GET", "/encoding/no-charset"), transport())
    assert response.headers["Content-Type"] == "text/plain"
    assert response.status_code == 200
    assert response.encoding is None
    assert response.text() == "Hello, world!"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_response_no_charset_with_iso_8859_1_content(send_request, transport):
    """
    We don't support iso-8859-1 by default following conversations
    about encoding flow
    """
    response = send_request(HttpRequest("GET", "/encoding/iso-8859-1"), transport())
    assert response.text() == "Accented: �sterreich"
    assert response.encoding is None


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_json(send_request, transport):
    response = send_request(HttpRequest("GET", "/basic/json"), transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding is None


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_json_with_specified_encoding(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/json"), transport())
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_emoji(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/emoji"), transport())
    assert response.text() == "👩"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_emoji_family_with_skin_tone_modifier(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/emoji-family-skin-tone-modifier"), transport())
    assert response.text() == "👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_korean_nfc(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/korean"), transport())
    assert response.text() == "아가"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_urlencoded_content(send_request, transport):
    send_request(
        HttpRequest(
            "POST", "/urlencoded/pet/add/1", data={"pet_type": "dog", "pet_food": "meat", "name": "Fido", "pet_age": 42}
        ),
        transport(),
    )


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_files_content(send_request, transport):
    request = HttpRequest(
        "POST",
        "/multipart/basic",
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    send_request(request, transport())


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_data_and_files_content(send_request, transport):
    request = HttpRequest(
        "POST",
        "/multipart/data-and-files",
        data={"message": "Hello, world!"},
        files={"fileContent": io.BytesIO(b"<file content>")},
    )
    send_request(request, transport())


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_multipart_encode_non_seekable_filelike(send_request, transport):
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
    send_request(request, transport())


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_get_xml_basic(send_request, transport):
    request = HttpRequest(
        "GET",
        "/xml/basic",
    )
    response = send_request(request, transport())
    parsed_xml = ET.fromstring(response.text())
    assert parsed_xml.tag == "slideshow"
    attributes = parsed_xml.attrib
    assert attributes["title"] == "Sample Slide Show"
    assert attributes["date"] == "Date of publication"
    assert attributes["author"] == "Yours Truly"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_put_xml_basic(send_request, transport):

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

    request = HttpRequest(
        "PUT",
        "/xml/basic",
        content=ET.fromstring(basic_body),
    )
    send_request(request, transport())


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_text_and_encoding(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/emoji"), transport())
    assert response.content == "👩".encode("utf-8")
    assert response.text() == "👩"

    # try setting encoding as a property
    response.encoding = "utf-16"
    assert response.text() == "鿰ꦑ" == response.content.decode(response.encoding)

    # assert latin-1 changes text decoding without changing encoding property
    assert response.text("latin-1") == "ð\x9f\x91©" == response.content.decode("latin-1")
    assert response.encoding == "utf-16"


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_passing_encoding_to_text(send_request, transport):
    response = send_request(HttpRequest("GET", "/encoding/emoji"), transport())
    assert response.content == "👩".encode("utf-8")
    assert response.text() == "👩"

    # pass in different encoding
    assert response.text("latin-1") == "ð\x9f\x91©"

    # check response.text() still gets us the old value
    assert response.text() == "👩"


def test_initialize_response_abc():
    with pytest.raises(TypeError) as ex:
        HttpResponse()
    assert "Can't instantiate abstract class" in str(ex)


@pytest.mark.parametrize("transport", SYNC_TRANSPORTS)
def test_readonly(send_request, transport):
    """Make sure everything that is readonly is readonly"""
    response = send_request(HttpRequest("GET", "/health"), transport())
    readonly_checks(response)
