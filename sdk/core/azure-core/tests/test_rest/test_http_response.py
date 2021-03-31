# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!
import json
import sys
import pytest
import requests
from azure.core.pipeline.transport import RequestsTransportResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.exceptions import HttpResponseError
from typing import Any, Dict

def _create_http_response(status_code=None, request=None, headers=None, content=None):
    # type: (int, Any, Dict[str, Any], bytes) -> HttpResponse
    # https://github.com/psf/requests/blob/67a7b2e8336951d527e223429672354989384197/requests/adapters.py#L255

    req_response = requests.Response()
    req_response._content = content
    req_response._content_consumed = True
    req_response.status_code = status_code
    req_response.reason = 'OK'
    if headers:
        # req_response.headers is type CaseInsensitiveDict
        req_response.headers.update(headers)
    req_response.encoding = requests.utils.get_encoding_from_headers(req_response.headers)

    response = RequestsTransportResponse(
        None, # Don't need a request here
        req_response
    )

    return HttpResponse(
        status_code=response.status_code,
        request=request,
        _internal_response=response
    )

def test_rest_response():
    response = _create_http_response(
        status_code=200,
        content=b"Hello, world!",
        request=HttpRequest("GET", "https://example.org"),
    )

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "https://example.org"
    response.raise_for_status()


def test_rest_response_content():
    response = _create_http_response(status_code=200, content=b"Hello, world!")

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    response.raise_for_status()


def test_rest_response_text():
    response = _create_http_response(200, content=b"Hello, world!", headers={
        "Content-Length": "13",
        "Content-Type": "text/plain; charset=utf-8",
    })

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    assert response.headers == {
        "Content-Length": "13",
        "Content-Type": "text/plain; charset=utf-8",
    }
    response.raise_for_status()


def test_rest_response_html():
    response = _create_http_response(200, content=b"<html><body>Hello, world!</html></body>")

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "<html><body>Hello, world!</html></body>"
    response.raise_for_status()

def test_rest_raise_for_status():
    request = HttpRequest("GET", "https://example.org")

    response = _create_http_response(200, request=request)
    response.raise_for_status()

    response = _create_http_response(403, request=request)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = _create_http_response(500, request=request)
    with pytest.raises(HttpResponseError):
        response.raise_for_status()


def test_rest_response_repr():
    headers = {"Content-Type": "text-plain"}
    response = _create_http_response(
        200,
        content=b"Hello, world!",
        headers=headers
    )
    assert repr(response) == "<HttpResponse: 200 OK, Content-Type: text-plain>"

def test_rest_response_content_type_encoding():
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    headers = {"Content-Type": "text-plain; charset=latin-1"}
    content = u"Latin 1: ÿ".encode("latin-1")
    response = _create_http_response(
        200,
        content=content,
        headers=headers,
    )
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding == "latin-1"


def test_rest_response_autodetect_encoding():
    """
    Autodetect encoding if there is no Content-Type header.
    """
    content = u"おはようございます。".encode("utf-8")
    response = _create_http_response(
        200,
        content=content,
    )
    assert response.text == u"おはようございます。"
    assert response.encoding is None

@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="the deserialization is weird if we first pass an invalid charset for 27")
def test_rest_response_fallback_to_autodetect():
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    headers = {"Content-Type": "text-plain; charset=invalid-codec-name"}
    content = u"おはようございます。".encode("utf-8")
    response = _create_http_response(
        200,
        content=content,
        headers=headers,
    )
    assert response.text == u"おはようございます。"
    assert response.encoding is None


def test_rest_response_no_charset_with_ascii_content():
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    content = b"Hello, world!"
    headers = {"Content-Type": "text/plain"}
    response = _create_http_response(
        200,
        content=content,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.encoding is None
    assert response.text == "Hello, world!"


def test_rest_response_no_charset_with_iso_8859_1_content():
    """
    A response with ISO 8859-1 encoded content should decode correctly,
    even with no charset specified.
    """
    content = u"Accented: Österreich".encode("iso-8859-1")
    headers = {"Content-Type": "text/plain"}
    response = _create_http_response(
        200,
        content=content,
        headers=headers,
    )
    assert response.text == u"Accented: Österreich"
    assert response.encoding is None

def test_rest_response_set_explicit_encoding():
    headers = {
        "Content-Type": "text-plain; charset=utf-8"
    }  # Deliberately incorrect charset
    response = _create_http_response(
        200,
        content=u"Latin 1: ÿ".encode("latin-1"),
        headers=headers,
    )
    response.encoding = "latin-1"
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding == "latin-1"

def test_rest_json():
    data = {"greeting": "hello", "recipient": "world"}
    content = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    response = _create_http_response(
        200,
        content=content,
        headers=headers,
    )
    assert response.json() == data

# NOTE: This works in async, not sync. Seems requests can't handle this, but aiohttp can
# def test_rest_json_with_specified_encoding():
#     data = {"greeting": "hello", "recipient": "world"}
#     content = json.dumps(data).encode("utf-16")
#     headers = {"Content-Type": "application/json, charset=utf-16"}
#     response = _create_http_response(
#         200,
#         content=content,
#         headers=headers,
#     )
#     assert response.json() == data

def test_rest_response_with_unset_request():
    response = _create_http_response(200, content=b"Hello, world!")

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    response.raise_for_status()


def test_rest_set_request_after_init():
    response = _create_http_response(200, content=b"Hello, world!")

    response.request = HttpRequest("GET", "https://www.example.org")

    assert response.request.method == "GET"
    assert response.request.url == "https://www.example.org"


def test_rest_cannot_access_unset_request():
    response = _create_http_response(200, content=b"Hello, world!")

    with pytest.raises(RuntimeError):
        response.request

def test_rest_emoji():
    response = _create_http_response(200, content=u"👩".encode("utf-16"))
    assert response.text == u"👩"

def test_rest_emoji_family_with_skin_tone_modifier():
    headers = {
        "Content-Type": "text-plain; charset=utf-16"
    }
    response = _create_http_response(200, headers=headers, content=u"👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987".encode("utf-16"))
    assert response.text == u"👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"

def test_rest_korean_nfc():
    response = _create_http_response(200, content=u"아가".encode("utf-8"))
    assert response.text == u"아가"