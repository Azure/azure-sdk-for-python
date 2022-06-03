# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
from collections import OrderedDict
import sys

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.pipeline.transport import HttpResponse as PipelineTransportHttpResponse, RequestsTransport
from azure.core.pipeline.transport._base import HttpTransport, _deserialize_response, _urljoin
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.pipeline import Pipeline
from azure.core.exceptions import HttpResponseError
import logging
import pytest
from utils import HTTP_REQUESTS, request_and_responses_product, HTTP_CLIENT_TRANSPORT_RESPONSES, create_transport_response
from azure.core.rest._http_response_impl import HttpResponseImpl as RestHttpResponseImpl
from azure.core.pipeline._tools import is_rest


class PipelineTransportMockResponse(PipelineTransportHttpResponse):
    def __init__(self, request, body, content_type):
        super(PipelineTransportMockResponse, self).__init__(request, None)
        self._body = body
        self.content_type = content_type

    def body(self):
        return self._body

class RestMockResponse(RestHttpResponseImpl):
    def __init__(self, request, body, content_type):
        super(RestMockResponse, self).__init__(
            request=request,
            internal_response=None,
            content_type=content_type,
            block_size=None,
            status_code=200,
            reason="OK",
            headers={},
            stream_download_generator=None,
        )
        # the impl takes in a lot more kwargs. It's not public and is a
        # helper implementation shared across our azure core transport responses
        self._body = body

    def body(self):
        return self._body

    @property
    def content(self):
        return self._body

MOCK_RESPONSES = [PipelineTransportMockResponse, RestMockResponse]

@pytest.mark.skipif(sys.version_info < (3, 6), reason="Multipart serialization not supported on 2.7 + dict order not deterministic on 3.5")
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_http_request_serialization(http_request):
    # Method + Url
    request = http_request("DELETE", "/container0/blob0")
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        # No headers
        b'\r\n'
    )
    assert serialized == expected

    # Method + Url + Headers
    request = http_request(
        "DELETE",
        "/container0/blob0",
        # Use OrderedDict to get consistent test result on 3.5 where order is not guaranteed
        headers=OrderedDict({
            "x-ms-date": "Thu, 14 Jun 2018 16:46:54 GMT",
            "Authorization": "SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=", # fake key suppressed in credscan
            "Content-Length": "0",
        })
    )
    serialized = request.serialize()

    expected = (
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'Authorization: SharedKey account:G4jjBXA7LI/RnWKIOQ8i9xH4p76pAQ+4Fs4R1VxasaE=\r\n' # fake key suppressed in credscan
        b'Content-Length: 0\r\n'
        b'\r\n'
    )
    assert serialized == expected


    # Method + Url + Headers + Body
    request = http_request(
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


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_url_join(http_request):
    assert _urljoin('devstoreaccount1', '') == 'devstoreaccount1/'
    assert _urljoin('devstoreaccount1', 'testdir/') == 'devstoreaccount1/testdir/'
    assert _urljoin('devstoreaccount1/', '') == 'devstoreaccount1/'
    assert _urljoin('devstoreaccount1/', 'testdir/') == 'devstoreaccount1/testdir/'


@pytest.mark.parametrize("http_request,http_response", request_and_responses_product(HTTP_CLIENT_TRANSPORT_RESPONSES))
def test_http_client_response(port, http_request, http_response):
    # Create a core request
    request = http_request("GET", "http://localhost:{}".format(port))

    # Fake a transport based on http.client
    conn = HTTPConnection("localhost", port)
    conn.request("GET", "/get")
    r1 = conn.getresponse()

    response = create_transport_response(http_response, request, r1)
    if is_rest(http_response):
        response.read()

    # Don't assume too much in those assert, since we reach a real server
    assert response.internal_response is r1
    assert response.reason is not None
    assert isinstance(response.status_code, int)
    assert len(response.headers.keys()) != 0
    assert len(response.text()) != 0
    assert "content-type" in response.headers
    assert "Content-Type" in response.headers


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_response_deserialization(http_request):

    # Method + Url
    request = http_request("DELETE", "/container0/blob0")
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
    request = http_request(
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

@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_response_deserialization_utf8_bom(http_request):

    request = http_request("DELETE", "/container0/blob0")
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_context(http_request):
    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_one_changeset(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    requests = [
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    ]

    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        *requests,
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_multiple_changesets(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset1 = http_request("", "")
    changeset1.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    changeset2 = http_request("", "")
    changeset2.set_multipart_mixed(
        http_request("DELETE", "/container2/blob2"),
        http_request("DELETE", "/container3/blob3"),
        policies=[header_policy],
        boundary="changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314"
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_combination_changeset_first(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset,
        http_request("DELETE", "/container2/blob2"),
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_combination_changeset_last(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container1/blob1"),
        http_request("DELETE", "/container2/blob2"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_multipart_send_with_combination_changeset_middle(http_request):

    transport = mock.MagicMock(spec=HttpTransport)

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container1/blob1"),
        policies=[header_policy],
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        changeset,
        http_request("DELETE", "/container2/blob2"),
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive(http_request, mock_response):

    class ResponsePolicy(object):
        def on_response(self, request, response):
            # type: (PipelineRequest, PipelineResponse) -> None
            response.http_response.headers['x-ms-fun'] = 'true'

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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

    response = mock_response(
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

@pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
def test_raise_for_status_bad_response(mock_response):
    response = mock_response(request=None, body=None, content_type=None)
    response.status_code = 400
    with pytest.raises(HttpResponseError):
        response.raise_for_status()

@pytest.mark.parametrize("mock_response", MOCK_RESPONSES)
def test_raise_for_status_good_response(mock_response):
    response = mock_response(request=None, body=None, content_type=None)
    response.status_code = 200
    response.raise_for_status()


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_one_changeset(http_request, mock_response):

    changeset = http_request(None, None)
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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

    response = mock_response(
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_multiple_changesets(http_request, mock_response):

    changeset1 = http_request(None, None)
    changeset1.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    )
    changeset2 = http_request(None, None)
    changeset2.set_multipart_mixed(
        http_request("DELETE", "/container2/blob2"),
        http_request("DELETE", "/container3/blob3")
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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

    response = mock_response(
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_combination_changeset_first(http_request, mock_response):

    changeset = http_request(None, None)
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(changeset, http_request("DELETE", "/container2/blob2"))
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

    response = mock_response(
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_combination_changeset_middle(http_request, mock_response):

    changeset = http_request(None, None)
    changeset.set_multipart_mixed(http_request("DELETE", "/container1/blob1"))

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        changeset,
        http_request("DELETE", "/container2/blob2")
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

    response = mock_response(
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_combination_changeset_last(http_request, mock_response):

    changeset = http_request(None, None)
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container1/blob1"),
        http_request("DELETE", "/container2/blob2")
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(http_request("DELETE", "/container0/blob0"), changeset)

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

    response = mock_response(
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


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_multipart_receive_with_bom(http_request, mock_response):

    req0 = http_request("DELETE", "/container0/blob0")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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

    response = mock_response(
        request,
        body_as_bytes,
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    response = response.parts()
    assert len(response) == 1

    res0 = response[0]
    assert res0.status_code == 400
    assert res0.body().startswith(b'\xef\xbb\xbf')


@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
def test_recursive_multipart_receive(http_request, mock_response):
    req0 = http_request("DELETE", "/container0/blob0")
    internal_req0 = http_request("DELETE", "/container0/blob0")
    req0.set_multipart_mixed(internal_req0)

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
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

    response = mock_response(
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


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_timeout(caplog, port, http_request):
    transport = RequestsTransport()

    request = http_request("GET", "http://localhost:{}/basic/string".format(port))

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=100)

    assert "Tuple timeout setting is deprecated" not in caplog.text


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_tuple_timeout(caplog, port, http_request):
    transport = RequestsTransport()

    request = http_request("GET", "http://localhost:{}/basic/string".format(port))

    with caplog.at_level(logging.WARNING, logger="azure.core.pipeline.transport"):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100))

    assert "Tuple timeout setting is deprecated" in caplog.text


@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
def test_conflict_timeout(caplog, port, http_request):
    transport = RequestsTransport()

    request = http_request("GET", "http://localhost:{}/basic/string".format(port))

    with pytest.raises(ValueError):
        with Pipeline(transport) as pipeline:
            pipeline.run(request, connection_timeout=(100, 100), read_timeout = 100)
