# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
from collections import OrderedDict
import time
import sys
import json

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.pipeline.transport import HttpRequest, HttpResponse, RequestsTransport
from azure.core.pipeline.transport._base import HttpClientTransportResponse, HttpTransport, _deserialize_response, _urljoin
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.pipeline import Pipeline
from azure.core.exceptions import HttpResponseError
import logging
import pytest


class MockResponse(HttpResponse):
    def __init__(self, request, body, content_type):
        super(MockResponse, self).__init__(request, None)
        self._body = body
        self.content_type = content_type

    def body(self):
        return self._body

@pytest.mark.skipif(sys.version_info < (3, 6), reason="Multipart serialization not supported on 2.7 + dict order not deterministic on 3.5")
def test_http_request_serialization():
    # Method + Url
    request = HttpRequest("DELETE", "/container0/blob0")
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        # No headers
        b'\r\n'
    )
    assert serialized == expected

    # Method + Url + Headers
    request = HttpRequest(
        "DELETE",
        "/container0/blob0",
        # Use OrderedDict to get consistent test result on 3.5 where order is not guaranted
        headers=OrderedDict({
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
            "Authorization": "SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=",
            "Content-Length": "0",
        })
    )
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Authorization: SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=\r\n'
        b'Content-Length: 0\r\n'
        b'\r\n'
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


def test_url_join():
    assert _urljoin('devstoreaccount1', '') == 'devstoreaccount1/'
    assert _urljoin('devstoreaccount1', 'testdir/') == 'devstoreaccount1/testdir/'
    assert _urljoin('devstoreaccount1/', '') == 'devstoreaccount1/'
    assert _urljoin('devstoreaccount1/', 'testdir/') == 'devstoreaccount1/testdir/'


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
    assert isinstance(response.status_code, int)
    assert len(response.headers.keys()) != 0
    assert len(response.text()) != 0
    assert "content-type" in response.headers
    assert "Content-Type" in response.headers


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

    assert isinstance(response.status_code, int)
    assert response.reason == "OK"
    assert response.headers == {
        'x-ms-request-id': '778fdc83-801e-0000-62ff-0334671e284f',
        'x-ms-version': '2018-11-09'
    }
    assert response.text() == "I am groot"

def test_response_deserialization_utf8_bom():

    request = HttpRequest("DELETE", "/container0/blob0")
    body = (
        b'HTTP/1.1 400 One of the request inputs is not valid.\r\n'
        b'x-ms-error-code: InvalidInput\r\n'
        b'x-ms-request-id: 5f3f9f2f-e01e-00cc-6eb1-6d00b5000000\r\n'
        b'x-ms-version: 2019-02-02\r\n'
        b'Content-Length: 220\r\n'
        b'Content-Type: application/xml\r\n'
        b'Server: Windows-Azure-Blob/1.0\r\n'
        b'\r\n'
        b'\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>\n<Error><Code>InvalidInput</Code><Message>One'
        b'of the request inputs is not valid.\nRequestId:5f3f9f2f-e01e-00cc-6eb1-6d00b5000000\nTime:2019-09-17T23:44:07.4671860Z</Message></Error>'
    )
    response = _deserialize_response(body, request)
    assert response.body().startswith(b'\xef\xbb\xbf')


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525" # Fix it so test are deterministic
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_context():
    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525", # Fix it so test are deterministic
        headers={'Accept': 'application/json'}
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Accept: application/json\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Accept: application/json\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_one_changeset():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    requests = [
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1")
    ]

    changeset = HttpRequest("", "")
    changeset.set_multipart_mixed(
        *requests,
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset,
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525",
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_multiple_changesets():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset1 = HttpRequest("", "")
    changeset1.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    changeset2 = HttpRequest("", "")
    changeset2.set_multipart_mixed(
        HttpRequest("DELETE", "/container2/blob2"),
        HttpRequest("DELETE", "/container3/blob3"),
        policies=[header_policy],
        boundary="changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314"
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset1,
        changeset2,
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525",
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'DELETE /container2/blob2 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 3\r\n'
        b'\r\n'
        b'DELETE /container3/blob3 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_combination_changeset_first():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = HttpRequest("", "")
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset,
        HttpRequest("DELETE", "/container2/blob2"),
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'DELETE /container2/blob2 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )

@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_combination_changeset_last():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = HttpRequest("", "")
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container1/blob1"),
        HttpRequest("DELETE", "/container2/blob2"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        changeset,
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'DELETE /container2/blob2 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )

@pytest.mark.skipif(sys.version_info < (3, 0), reason="Multipart serialization not supported on 2.7")
def test_multipart_send_with_combination_changeset_middle():

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = HttpRequest("", "")
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        changeset,
        HttpRequest("DELETE", "/container2/blob2"),
        policies=[header_policy],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    with Pipeline(transport) as pipeline:
        pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: multipart/mixed; boundary=changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'DELETE /container2/blob2 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


def test_multipart_receive():

    class ResponsePolicy(object):
        def on_response(self, request, response):
            # type: (PipelineRequest, PipelineResponse) -> None
            response.http_response.headers['x-ms-fun'] = 'true'

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[ResponsePolicy()]
    )

    body_as_str = (
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 0\r\n"
        "\r\n"
        "HTTP/1.1 202 Accepted\r\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n"
        "x-ms-version: 2018-11-09\r\n"
        "\r\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 2\r\n"
        "\r\n"
        "HTTP/1.1 404 The specified blob does not exist.\r\n"
        "x-ms-error-code: BlobNotFound\r\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e2852\r\n"
        "x-ms-version: 2018-11-09\r\n"
        "Content-Length: 216\r\n"
        "Content-Type: application/xml\r\n"
        "\r\n"
        '<?xml version="1.0" encoding="utf-8"?>\r\n'
        "<Error><Code>BlobNotFound</Code><Message>The specified blob does not exist.\r\n"
        "RequestId:778fdc83-801e-0000-62ff-0334671e2852\r\n"
        "Time:2018-06-14T16:46:54.6040685Z</Message></Error>\r\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--"
    )

    response = MockResponse(
        request,
        body_as_str.encode('ascii'),
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    response = response.parts()

    assert len(response) == 2

    res0 = response[0]
    assert res0.status_code == 202
    assert res0.headers['x-ms-fun'] == 'true'

    res1 = response[1]
    assert res1.status_code == 404
    assert res1.headers['x-ms-fun'] == 'true'

def test_raise_for_status_bad_response():
    response = MockResponse(request=None, body=None, content_type=None)
    response.status_code = 400
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

def test_raise_for_status_good_response():
    response = MockResponse(request=None, body=None, content_type=None)
    response.status_code = 200
    response.raise_for_status()


def test_multipart_receive_with_one_changeset():

    changeset = HttpRequest(None, None)
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1")
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(changeset)

    body_as_bytes = (
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'HTTP/1.1 202 Accepted\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'HTTP/1.1 202 Accepted\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--\r\n'
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    parts = []
    for part in response.parts():
        parts.append(part)
    assert len(parts) == 2

    res0 = parts[0]
    assert res0.status_code == 202


def test_multipart_receive_with_multiple_changesets():

    changeset1 = HttpRequest(None, None)
    changeset1.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1")
    )
    changeset2 = HttpRequest(None, None)
    changeset2.set_multipart_mixed(
        HttpRequest("DELETE", "/container2/blob2"),
        HttpRequest("DELETE", "/container3/blob3")
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(changeset1, changeset2)
    body_as_bytes = (
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'HTTP/1.1 200\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'HTTP/1.1 202\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314"\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'HTTP/1.1 404\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 3\r\n'
        b'\r\n'
        b'HTTP/1.1 409\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--\r\n'
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    parts = []
    for part in response.parts():
        parts.append(part)
    assert len(parts) == 4
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404
    assert parts[3].status_code == 409


def test_multipart_receive_with_combination_changeset_first():

    changeset = HttpRequest(None, None)
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        HttpRequest("DELETE", "/container1/blob1")
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(changeset, HttpRequest("DELETE", "/container2/blob2"))
    body_as_bytes = (
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'HTTP/1.1 200\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'HTTP/1.1 202\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'HTTP/1.1 404\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--\r\n'
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    parts = []
    for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404


def test_multipart_receive_with_combination_changeset_middle():

    changeset = HttpRequest(None, None)
    changeset.set_multipart_mixed(HttpRequest("DELETE", "/container1/blob1"))

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        HttpRequest("DELETE", "/container0/blob0"),
        changeset,
        HttpRequest("DELETE", "/container2/blob2")
    )
    body_as_bytes = (
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'HTTP/1.1 200\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'HTTP/1.1 202\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'HTTP/1.1 404\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--\r\n'
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    parts = []
    for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404


def test_multipart_receive_with_combination_changeset_last():

    changeset = HttpRequest(None, None)
    changeset.set_multipart_mixed(
        HttpRequest("DELETE", "/container1/blob1"),
        HttpRequest("DELETE", "/container2/blob2")
    )

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(HttpRequest("DELETE", "/container0/blob0"), changeset)

    body_as_bytes = (
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'HTTP/1.1 200\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n'
        b'Content-Type: multipart/mixed; boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'HTTP/1.1 202\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'HTTP/1.1 404\r\n'
        b'x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n'
        b'x-ms-version: 2018-11-09\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--\r\n'
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    parts = []
    for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404


def test_multipart_receive_with_bom():

    req0 = HttpRequest("DELETE", "/container0/blob0")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(req0)
    body_as_bytes = (
        b"--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\n"
        b"Content-Type: application/http\n"
        b"Content-Transfer-Encoding: binary\n"
        b"Content-ID: 0\n"
        b'\r\n'
        b'HTTP/1.1 400 One of the request inputs is not valid.\r\n'
        b'Content-Length: 220\r\n'
        b'Content-Type: application/xml\r\n'
        b'Server: Windows-Azure-Blob/1.0\r\n'
        b'\r\n'
        b'\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>\n<Error><Code>InvalidInput</Code><Message>One'
        b'of the request inputs is not valid.\nRequestId:5f3f9f2f-e01e-00cc-6eb1-6d00b5000000\nTime:2019-09-17T23:44:07.4671860Z</Message></Error>\n'
        b"--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--"
    )

    response = MockResponse(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    response = response.parts()
    assert len(response) == 1

    res0 = response[0]
    assert res0.status_code == 400
    assert res0.body().startswith(b'\xef\xbb\xbf')


def test_recursive_multipart_receive():
    req0 = HttpRequest("DELETE", "/container0/blob0")
    internal_req0 = HttpRequest("DELETE", "/container0/blob0")
    req0.set_multipart_mixed(internal_req0)

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(req0)
    internal_body_as_str = (
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 0\r\n"
        "\r\n"
        "HTTP/1.1 400 Accepted\r\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\r\n"
        "x-ms-version: 2018-11-09\r\n"
        "\r\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--"
    )

    body_as_str = (
        "--batchresponse_8d5f5bcd-2cb5-44bb-91b5-e9a722e68cb6\r\n"
        "Content-Type: application/http\r\n"
        "Content-ID: 0\r\n"
        "\r\n"
        "HTTP/1.1 202 Accepted\r\n"
        "Content-Type: multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\r\n"
        "\r\n"
        "{}"
        "--batchresponse_8d5f5bcd-2cb5-44bb-91b5-e9a722e68cb6--"
    ).format(internal_body_as_str)

    response = MockResponse(
        request,
        body_as_str.encode('ascii'),
        "multipart/mixed; boundary=batchresponse_8d5f5bcd-2cb5-44bb-91b5-e9a722e68cb6"
    )

    response = response.parts()
    assert len(response) == 1

    res0 = response[0]
    assert res0.status_code == 202

    internal_response = res0.parts()
    assert len(internal_response) == 1

    internal_response0 = internal_response[0]
    assert internal_response0.status_code == 400


def test_close_unopened_transport():
    transport = RequestsTransport()
    transport.close()

def test_timeout(caplog):
    transport = RequestsTransport()

    request = HttpRequest("GET", "https://www.bing.com")

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=100)

    assert "Tuple timeout setting is deprecated" not in caplog.text

def test_tuple_timeout(caplog):
    transport = RequestsTransport()

    request = HttpRequest("GET", "https://www.bing.com")

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100))

    assert "Tuple timeout setting is deprecated" in caplog.text

def test_conflict_timeout(caplog):
    transport = RequestsTransport()

    request = HttpRequest("GET", "https://www.bing.com")

    with pytest.raises(ValueError):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100), read_timeout = 100)
