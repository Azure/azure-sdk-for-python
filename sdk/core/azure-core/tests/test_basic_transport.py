# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from six.moves.http_client import HTTPConnection
import time

from azure.core.pipeline.transport import HttpRequest, HttpResponse, RequestsTransport
from azure.core.pipeline.transport.base import HttpClientTransportResponse, _deserialize_response, MultiPartHelper
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.pipeline import Pipeline


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


def test_multipart_send():

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[header_policy]
    )

    helper = MultiPartHelper(request)
    helper.prepare_request()

    # FIXME Boundary is random, so need to improve this test with a regexp or something
    assert request.body == (
        b'--===============6566992931842418154==\n'
        b'content-type: application/http\n'
        b'\n'
        b'DELETE /container0/blob0 HTTP/1.1\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\n\n\n'
        b'--===============6566992931842418154==\n'
        b'content-type: application/http\n'
        b'\n'
        b'DELETE /container1/blob1 HTTP/1.1\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\n\n\n'
        b'--===============6566992931842418154==--\n'
    )

def test_multipart_receive():

    class MockResponse(HttpResponse):
        def __init__(self, body, content_type):
            super(MockResponse, self).__init__(None, None)
            self._body = body
            self.content_type = content_type

        def body(self):
            return self._body

    class ResponsePolicy(object):
        def on_response(self, request, response):
            # type: (PipelineRequest, PipelineResponse) -> None
            response.http_response.headers['x-ms-fun'] = 'true'

    body_as_str = (
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\n"
        "Content-Type: application/http\n"
        "Content-ID: 0\n"
        "\n"
        "HTTP/1.1 202 Accepted\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f\n"
        "x-ms-version: 2018-11-09\n"
        "\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed\n"
        "Content-Type: application/http\n"
        "Content-ID: 2\n"
        "\n"
        "HTTP/1.1 404 The specified blob does not exist.\n"
        "x-ms-error-code: BlobNotFound\n"
        "x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e2852\n"
        "x-ms-version: 2018-11-09\n"
        "Content-Length: 216\n"
        "Content-Type: application/xml\n"
        "\n"
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<Error><Code>BlobNotFound</Code><Message>The specified blob does not exist.\n"
        "RequestId:778fdc83-801e-0000-62ff-0334671e2852\n"
        "Time:2018-06-14T16:46:54.6040685Z</Message></Error>\n"
        "--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--"
    )

    response = MockResponse(
        body_as_str.encode('ascii'),
        "multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed"
    )

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")

    request = HttpRequest("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[ResponsePolicy()]
    )

    helper = MultiPartHelper(request)

    response = helper.parse_response(response)

    res0 = response[0]
    assert res0.status_code == 202
    assert res0.headers['x-ms-fun'] == 'true'

    res1 = response[1]
    assert res1.status_code == 404
    assert res1.headers['x-ms-fun'] == 'true'

def test_pipeline_full_scenario():

    # To get this test to zork, create a mocky.io:
    # Content type: multipart/mixed; boundary=batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed
    # Body:
    """
--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed
Content-Type: application/http
Content-ID: 0

HTTP/1.1 202 Accepted
x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e284f
x-ms-version: 2018-11-09

--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed
Content-Type: application/http
Content-ID: 1

HTTP/1.1 202 Accepted
x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e2851
x-ms-version: 2018-11-09

--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed
Content-Type: application/http
Content-ID: 2

HTTP/1.1 404 The specified blob does not exist.
x-ms-error-code: BlobNotFound
x-ms-request-id: 778fdc83-801e-0000-62ff-0334671e2852
x-ms-version: 2018-11-09
Content-Length: 216
Content-Type: application/xml

<?xml version="1.0" encoding="utf-8"?>
<Error><Code>BlobNotFound</Code><Message>The specified blob does not exist.
RequestId:778fdc83-801e-0000-62ff-0334671e2852
Time:2018-06-14T16:46:54.6040685Z</Message></Error>
--batchresponse_66925647-d0cb-4109-b6d3-28efe3e1e5ed--
"""

    header_policy = HeadersPolicy({
        'x-ms-date': 'Thu, 14 Jun 2018 16:46:54 GMT'
    })

    req0 = HttpRequest("DELETE", "/container0/blob0")
    req1 = HttpRequest("DELETE", "/container1/blob1")
    req2 = HttpRequest("DELETE", "/container2/blob2")

    request = HttpRequest("GET", "http://www.mocky.io/v2/5d72e4892f0000ce9c7d4ec1")
    request.set_multipart_mixed(
        req0,
        req1,
        req2,
        policies=[header_policy]
    )

    with Pipeline(RequestsTransport(), policies=[]) as pipeline:
        response = pipeline.run(request)

    assert len(response.context['MULTIPART_RESPONSE']) == 3
    assert response.context['MULTIPART_RESPONSE'][2].status_code == 404
