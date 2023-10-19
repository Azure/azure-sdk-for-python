# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from corehttp.transport.aiohttp import AioHttpTransport

import aiohttp

import pytest
from utils import HTTP_REQUESTS, AIOHTTP_TRANSPORT_RESPONSES, create_transport_response


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_basic_aiohttp(port, http_request):

    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    async with AioHttpTransport() as sender:
        response = await sender.send(request)
        assert response.content is not None

    assert sender.session is None
    assert isinstance(response.status_code, int)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_aiohttp_auto_headers(port, http_request):

    request = http_request("POST", "http://localhost:{}/basic/string".format(port))
    async with AioHttpTransport() as sender:
        response = await sender.send(request)
        auto_headers = response._internal_response.request_info.headers
        assert "Content-Type" not in auto_headers


def _create_aiohttp_response(http_response, body_bytes, headers=None):
    class MockAiohttpClientResponse(aiohttp.ClientResponse):
        def __init__(self, body_bytes, headers=None):
            self._body = body_bytes
            self._headers = headers
            self._cache = {}
            self.status = 200
            self.reason = "OK"

    req_response = MockAiohttpClientResponse(body_bytes, headers)

    response = create_transport_response(http_response, None, req_response)  # Don't need a request here
    response._content = body_bytes

    return response


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response", AIOHTTP_TRANSPORT_RESPONSES)
async def test_aiohttp_response_text(http_response):

    for encoding in ["utf-8", "utf-8-sig", None]:

        res = _create_aiohttp_response(http_response, b"\xef\xbb\xbf56", {"Content-Type": "text/plain"})
        await res.read()
        assert res.text(encoding) == "56", "Encoding {} didn't work".format(encoding)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response", AIOHTTP_TRANSPORT_RESPONSES)
async def test_aiohttp_response_decompression(http_response):
    # cSpell:disable
    res = _create_aiohttp_response(
        http_response,
        b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x04\x00\x8d\x8d\xb1n\xc30\x0cD"
        b"\xff\x85s\x14HVlY\xda\x8av.\n4\x1d\x9a\x8d\xa1\xe5D\x80m\x01\x12="
        b"\x14A\xfe\xbd\x92\x81d\xceB\x1c\xef\xf8\x8e7\x08\x038\xf0\xa67Fj+"
        b"\x946\x9d8\x0c4\x08{\x96(\x94mzkh\x1cM/a\x07\x94<\xb2\x1f>\xca8\x86"
        b"\xd9\xff0\x15\xb6\x91\x8d\x12\xb2\x15\xd2\x1c\x95q\xbau\xba\xdbk"
        b"\xd5(\xd9\xb5\xa7\xc2L\x98\xf9\x8d8\xc4\xe5U\xccV,3\xf2\x9a\xcb\xddg"
        b"\xe4o\xc6T\xdeVw\x9dgL\x7f\xe0n\xc0\x91q\x02'w0b\x98JZe^\x89|\xce\x9b"
        b"\x0e\xcbW\x8a\x97\xf4X\x97\xc8\xbf\xfeYU\x1d\xc2\x85\xfc\xf4@\xb7\xbe"
        b"\xf7+&$\xf6\xa9\x8a\xcb\x96\xdc\xef\xff\xaa\xa1\x1c\xf9$\x01\x00\x00",
        {"Content-Type": "text/plain", "Content-Encoding": "gzip"},
    )
    # cSpell:enable
    expect = (
        b'{"id":"e7877039-1376-4dcd-9b0a-192897cff780","createdDateTimeUtc":'
        b'"2021-05-07T17:35:36.3121065Z","lastActionDateTimeUtc":'
        b'"2021-05-07T17:35:36.3121069Z","status":"NotStarted",'
        b'"summary":{"total":0,"failed":0,"success":0,"inProgress":0,'
        b'"notYetStarted":0,"cancelled":0,"totalCharacterCharged":0}}'
    )
    assert res.content == expect, "Decompression didn't work"


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response", AIOHTTP_TRANSPORT_RESPONSES)
async def test_aiohttp_response_decompression_negative(http_response):
    import zlib

    # cSpell:disable
    res = _create_aiohttp_response(
        http_response,
        b"\xff\x85s\x14HVlY\xda\x8av.\n4\x1d\x9a\x8d\xa1\xe5D\x80m\x01\x12="
        b"\x14A\xfe\xbd\x92\x81d\xceB\x1c\xef\xf8\x8e7\x08\x038\xf0\xa67Fj+"
        b"\x946\x9d8\x0c4\x08{\x96(\x94mzkh\x1cM/a\x07\x94<\xb2\x1f>\xca8\x86"
        b"\xd9\xff0\x15\xb6\x91\x8d\x12\xb2\x15\xd2\x1c\x95q\xbau\xba\xdbk"
        b"\xd5(\xd9\xb5\xa7\xc2L\x98\xf9\x8d8\xc4\xe5U\xccV,3\xf2\x9a\xcb\xddg"
        b"\xe4o\xc6T\xdeVw\x9dgL\x7f\xe0n\xc0\x91q\x02'w0b\x98JZe^\x89|\xce\x9b"
        b"\x0e\xcbW\x8a\x97\xf4X\x97\xc8\xbf\xfeYU\x1d\xc2\x85\xfc\xf4@\xb7\xbe"
        b"\xf7+&$\xf6\xa9\x8a\xcb\x96\xdc\xef\xff\xaa\xa1\x1c\xf9$\x01\x00\x00",
        {"Content-Type": "text/plain", "Content-Encoding": "gzip"},
    )
    # cSpell:enable
    with pytest.raises(zlib.error):
        res.content()


@pytest.mark.parametrize("http_response", AIOHTTP_TRANSPORT_RESPONSES)
def test_repr(http_response):
    res = _create_aiohttp_response(http_response, b"\xef\xbb\xbf56", {"content-type": "text/plain"})

    class_name = "AsyncHttpResponse"
    assert repr(res) == f"<{class_name}: 200 OK, Content-Type: text/plain>"
