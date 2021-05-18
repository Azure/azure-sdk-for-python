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
from azure.core.pipeline.transport import RequestsTransport
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.exceptions import HttpResponseError
from typing import Any, Dict

def _create_http_response(request=None):
    internal_response = RequestsTransport().send(request._internal_request, stream=False)
    response = HttpResponse(
        request=request,
        _internal_response=internal_response
    )
    return response

def test_response():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/string"),
    )
    response.read()
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    assert response.request.method == "GET"
    assert response.request.url == "http://localhost:3000/basic/helloWorld/string"
    response.raise_for_status()


def test_response_content():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/bytes"),
    )
    response.read()
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    response.raise_for_status()


def test_response_text():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text"),
    )
    response.read()
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "Hello, world!"
    assert response.headers["Content-Length"] == '13'
    assert response.headers['Content-Type'] == "text/plain; charset=utf-8"
    assert response.content_type == "text/plain; charset=utf-8"
    response.raise_for_status()


def test_response_html():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/html"),
    )
    response.read()
    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.text == "<html><body>Hello, world!</html></body>"
    response.raise_for_status()

def test_raise_for_status():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text"),
    )
    response.raise_for_status()

    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/errors/403"),
    )
    assert response.status_code == 403
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/errors/500"),
    )
    assert response.status_code == 500
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

def test_response_repr():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/text")
    )
    assert repr(response) == "<HttpResponse: 200 OK, Content-Type: text/plain; charset=utf-8>"

def test_response_content_type_encoding():
    """
    Use the charset encoding in the Content-Type header if possible.
    """
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    response.raise_for_status()
    response.read()
    assert response.content_type == "text/plain; charset=latin-1"
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding == "latin-1"


def test_response_autodetect_encoding():
    """
    Autodetect encoding if there is no Content-Type header.
    """
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    response.read()

    # going to hack no content type response header being sent back
    response._internal_response.headers["Content-Type"] = None
    assert response.text == u'Latin 1: ÿ'
    assert response.encoding is None

def test_response_fallback_to_autodetect():
    """
    Fallback to autodetection if we get an invalid charset in the Content-Type header.
    """
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1")
    )
    response.read()

    # can't actually send incorrect charset from testserver, so overriding to bad charset
    response._internal_response.headers["Content-Type"] = "text-plain; charset=invalid-codec-name"
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding is None


def test_response_no_charset_with_ascii_content():
    """
    A response with ascii encoded content should decode correctly,
    even with no charset specified.
    """
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/helloWorld/string"),
    )
    response.read()

    # charset's will get added in real calls to testserver, so just changing content
    # type to remove charset
    response._internal_response.headers["Content-Type"] = "text/plain"

    assert response.status_code == 200
    assert response.encoding is None
    assert response.headers["Content-Type"] == "text/plain"
    assert response.text == "Hello, world!"


def test_response_no_charset_with_iso_8859_1_content():
    """
    A response with ISO 8859-1 encoded content should decode correctly,
    even with no charset specified.
    """
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/iso-8859-1"),
    )
    response.read()

    # charset's will get added in real calls to testserver, so just changing content
    # type to remove charset
    response._internal_response.headers["Content-Type"] = "text/plain"
    assert content == b'Accented: \xc3\x96sterreich'
    assert response.text == u"Accented: Österreich"
    assert response.encoding is None

def test_response_set_explicit_encoding():
    # Deliberately incorrect charset
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/latin-1-string-with-utf-8"),
    )
    response.read()
    response.encoding = "latin-1"
    assert response.text == u"Latin 1: ÿ"
    assert response.encoding == "latin-1"

def test_json():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/basic/json"),
    )
    response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}

def test_json_with_specified_encoding():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/json"),
    )
    response.read()
    assert response.json() == {"greeting": "hello", "recipient": "world"}
    assert response.encoding == "utf-16"

def test_emoji():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/emoji"),
    )
    response.read()
    assert response.text == u"👩"

def test_emoji_family_with_skin_tone_modifier():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/emoji-family-skin-tone-modifier"),
    )
    response.read()
    assert response.text == u"👩🏻‍👩🏽‍👧🏾‍👦🏿 SSN: 859-98-0987"

def test_korean_nfc():
    response = _create_http_response(
        request=HttpRequest("GET", "http://localhost:3000/encoding/korean"),
    )
    response.read()
    assert response.text == u"아가"