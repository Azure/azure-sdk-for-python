# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
import time

from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.transport.base import HttpClientTransportResponse, _deserialize_response


def test_http_request_serialization():
    # Method + Url
    request = HttpRequest("DELETE", "/container0/blob0")
    serialized = request.serialize()

    expected = b'DELETE /container0/blob0 HTTP/1.1\r\n\r\n'
    assert serialized == expected

    # Method + Url + Headers
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        headers={
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
            "Authorization": "SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=",
            "Content-Length": "0",
        }
    )
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Authorization: SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=\r\n'
        b'Content-Length: 0\r\n\r\n'
    )
    assert serialized == expected


    # Method + Url + Headers + Body
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        headers={
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
        },
    )
    request.set_bytes_body(b"I am groot")
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Content-Length: 10\r\n'
        b'\r\n'
        b'I am groot'
    )
    assert serialized == expected


def test_http_client_response():
    # Create a core request
    request = HttpRequest("GET", "www.httpbin.org")

    # Fake a transport based on http.client
    conn = HTTPConnection("www.httpbin.org")
    conn.request("GET", "/get")
    r1 = conn.getresponse()

    response = HttpClientTransportResponse(request, r1)

    # Don't assume too much in those assert, since we reach a real server
    assert response.internal_response is r1
    assert response.reason is not None
    assert response.status_code == 200
    assert len(response.headers.keys()) != 0
    assert len(response.text()) != 0


def test_response_deserialization():

    # Method + Url
    request = HttpRequest("DELETE", "/container0/blob0")
    body = (
        b'HTTP/1.1 202 Accepted\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
    )

    response = _deserialize_response(body, request)

    assert response.status_code == 202
    assert response.reason == "Accepted"
    assert response.headers == {
        'x-ms-request-id': '778fdc83-801e-0000-62ff-0334671e284f',
        'x-ms-version': '2018-11-09'
    }

    # Method + Url + Headers + Body
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        headers={
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
        },
    )
    request.set_bytes_body(b"I am groot")
    body = (
        b'HTTP/1.1 200 OK\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'I am groot'
    )

    response = _deserialize_response(body, request)

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.headers == {
        'x-ms-request-id': '778fdc83-801e-0000-62ff-0334671e284f',
        'x-ms-version': '2018-11-09'
    }
    assert response.text() == "I am groot"