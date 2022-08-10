# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport import AsyncHttpResponse as PipelineTransportAsyncHttpResponse, AsyncHttpTransport, AioHttpTransport
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl as RestAsyncHttpResponse
from azure.core.pipeline.policies import HeadersPolicy
from azure.core.pipeline import AsyncPipeline
from azure.core.exceptions import HttpResponseError
from utils import HTTP_REQUESTS, request_and_responses_product
import pytest
import sys


# transport = mock.MagicMock(spec=AsyncHttpTransport)
# MagicMock support async cxt manager only after 3.8
# https://github.com/python/cpython/pull/9296

class MockAsyncHttpTransport(AsyncHttpTransport):
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    async def open(self): pass
    async def close(self): pass
    async def send(self, request, **kwargs): pass


class PipelineTransportMockResponse(PipelineTransportAsyncHttpResponse):
    def __init__(self, request, body, content_type):
        super().__init__(request, None)
        self._body = body
        self.content_type = content_type

    def body(self):
        return self._body

class RestMockResponse(RestAsyncHttpResponse):
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
        self._content = body

    def body(self):
        return self._content

    @property
    def content(self):
        return self._content

MOCK_RESPONSES = [PipelineTransportMockResponse, RestMockResponse]

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_basic_options_aiohttp(port, http_request):

    request = http_request("OPTIONS", "http://localhost:{}/basic/string".format(port))
    async with AsyncPipeline(AioHttpTransport(), policies=[]) as pipeline:
        response = await pipeline.run(request)

    assert pipeline._transport.session is None
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send(http_request):
    transport = MockAsyncHttpTransport()

    class RequestPolicy(object):
        async def on_request(self, request):
            # type: (PipelineRequest) -> None
            request.http_request.headers['x-ms-date'] = 'Thu, 14 Jun 2018 16:46:54 GMT'

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[RequestPolicy()],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525" # Fix it so test are deterministic
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

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


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_context(http_request):

    transport = MockAsyncHttpTransport()
    header_policy = HeadersPolicy()

    class RequestPolicy(object):
        async def on_request(self, request):
            # type: (PipelineRequest) -> None
            request.http_request.headers['x-ms-date'] = 'Thu, 14 Jun 2018 16:46:54 GMT'

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[header_policy, RequestPolicy()],
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525", # Fix it so test are deterministic
        headers={'Accept': 'application/json'}
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
        b'Accept: application/json\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'Accept: application/json\r\n'
        b'x-ms-date: Thu, 14 Jun 2018 16:46:54 GMT\r\n'
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_one_changeset(http_request):
    transport = MockAsyncHttpTransport()
    requests = [
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    ]
    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        *requests,
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset,
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

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
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_multiple_changesets(http_request):
    transport = MockAsyncHttpTransport()
    changeset1 = http_request("", "")
    changeset1.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1"),
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    changeset2 = http_request("", "")
    changeset2.set_multipart_mixed(
        http_request("DELETE", "/container2/blob2"),
        http_request("DELETE", "/container3/blob3"),
        boundary="changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314"
    )

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset1,
        changeset2,
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525",
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

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
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
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
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 3\r\n'
        b'\r\n'
        b'DELETE /container3/blob3 HTTP/1.1\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_8b9e487e-a353-4dcb-a6f4-0688191e0314--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_combination_changeset_first(http_request):
    transport = MockAsyncHttpTransport()

    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1"),
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        changeset,
        http_request("DELETE", "/container2/blob2"),
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

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
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 1\r\n'
        b'\r\n'
        b'DELETE /container1/blob1 HTTP/1.1\r\n'
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
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_combination_changeset_last(http_request):
    transport = MockAsyncHttpTransport()
    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container1/blob1"),
        http_request("DELETE", "/container2/blob2"),
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        changeset,
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
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
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 2\r\n'
        b'\r\n'
        b'DELETE /container2/blob2 HTTP/1.1\r\n'
        b'\r\n'
        b'\r\n'
        b'--changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_multipart_send_with_combination_changeset_middle(http_request):
    transport = MockAsyncHttpTransport()
    changeset = http_request("", "")
    changeset.set_multipart_mixed(
        http_request("DELETE", "/container1/blob1"),
        boundary="changeset_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )
    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        changeset,
        http_request("DELETE", "/container2/blob2"),
        boundary="batch_357de4f7-6d0b-4e02-8cd2-6361411a9525"
    )

    async with AsyncPipeline(transport) as pipeline:
        await pipeline.run(request)

    assert request.body == (
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525\r\n'
        b'Content-Type: application/http\r\n'
        b'Content-Transfer-Encoding: binary\r\n'
        b'Content-ID: 0\r\n'
        b'\r\n'
        b'DELETE /container0/blob0 HTTP/1.1\r\n'
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
        b'\r\n'
        b'\r\n'
        b'--batch_357de4f7-6d0b-4e02-8cd2-6361411a9525--\r\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive(http_request, mock_response):

    class ResponsePolicy(object):
        def on_response(self, request, response):
            # type: (PipelineRequest, PipelineResponse) -> None
            response.http_response.headers['x-ms-fun'] = 'true'

    class AsyncResponsePolicy(object):
        async def on_response(self, request, response):
            # type: (PipelineRequest, PipelineResponse) -> None
            response.http_response.headers['x-ms-async-fun'] = 'true'

    req0 = http_request("DELETE", "/container0/blob0")
    req1 = http_request("DELETE", "/container1/blob1")

    request = http_request("POST", "http://account.blob.core.windows.net/?comp=batch")
    request.set_multipart_mixed(
        req0,
        req1,
        policies=[ResponsePolicy(), AsyncResponsePolicy()]
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

    parts = []
    async for part in response.parts():
        parts.append(part)

    assert len(parts) == 2

    res0 = parts[0]
    assert res0.status_code == 202
    assert res0.headers['x-ms-fun'] == 'true'
    assert res0.headers['x-ms-async-fun'] == 'true'

    res1 = parts[1]
    assert res1.status_code == 404
    assert res1.headers['x-ms-fun'] == 'true'
    assert res1.headers['x-ms-async-fun'] == 'true'


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_one_changeset(http_request, mock_response):
    changeset = http_request("", "")
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
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 2

    res0 = parts[0]
    assert res0.status_code == 202


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_multiple_changesets(http_request, mock_response):

    changeset1 = http_request("", "")
    changeset1.set_multipart_mixed(
        http_request("DELETE", "/container0/blob0"),
        http_request("DELETE", "/container1/blob1")
    )
    changeset2 = http_request("", "")
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
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 4
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404
    assert parts[3].status_code == 409


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_combination_changeset_first(http_request, mock_response):

    changeset = http_request("", "")
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
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404

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


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_combination_changeset_middle(http_request, mock_response):

    changeset = http_request("", "")
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
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_combination_changeset_last(http_request, mock_response):

    changeset = http_request("", "")
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
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 3
    assert parts[0].status_code == 200
    assert parts[1].status_code == 202
    assert parts[2].status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_multipart_receive_with_bom(http_request, mock_response):

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

    parts = []
    async for part in response.parts():
        parts.append(part)
    assert len(parts) == 1

    res0 = parts[0]
    assert res0.status_code == 400
    assert res0.body().startswith(b'\xef\xbb\xbf')


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request,mock_response", request_and_responses_product(MOCK_RESPONSES))
async def test_recursive_multipart_receive(http_request, mock_response):
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

    parts = []
    async for part in response.parts():
        parts.append(part)

    assert len(parts) == 1

    res0 = parts[0]
    assert res0.status_code == 202

    internal_parts = []
    async for part in res0.parts():
        internal_parts.append(part)
    assert len(internal_parts) == 1

    internal_response0 = internal_parts[0]
    assert internal_response0.status_code == 400


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Loop parameter is deprecated since Python 3.10")
def test_aiohttp_loop():
    import asyncio
    from azure.core.pipeline.transport import AioHttpTransport
    loop = asyncio.get_event_loop()
    with pytest.raises(ValueError):
        transport = AioHttpTransport(loop=loop)

def test_open_closed_aiohttp_transport():
    transport = AioHttpTransport()
    transport.close()
    transport.open()
    assert not transport.session
