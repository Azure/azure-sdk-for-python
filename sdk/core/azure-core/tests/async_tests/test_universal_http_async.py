#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------
import sys

from azure.core.pipeline.transport import (
    HttpRequest,
    AioHttpTransport,
    AioHttpTransportResponse,
    AsyncHttpTransport,
    AsyncioRequestsTransport,
    TrioRequestsTransport)

import aiohttp
import trio

import pytest
from unittest import mock


@pytest.mark.asyncio
async def test_basic_aiohttp():

    request = HttpRequest("GET", "https://www.bing.com/")
    async with AioHttpTransport() as sender:
        response = await sender.send(request)
        assert response.body() is not None

    assert sender.session is None
    assert isinstance(response.status_code, int)

@pytest.mark.asyncio
async def test_aiohttp_auto_headers():

    request = HttpRequest("POST", "https://www.bing.com/")
    async with AioHttpTransport() as sender:
        response = await sender.send(request)
        auto_headers = response.internal_response.request_info.headers
        assert 'Content-Type' not in auto_headers

@pytest.mark.asyncio
async def test_basic_async_requests():

    request = HttpRequest("GET", "https://www.bing.com/")
    async with AsyncioRequestsTransport() as sender:
        response = await sender.send(request)
        assert response.body() is not None

    assert isinstance(response.status_code, int)

@pytest.mark.asyncio
async def test_conf_async_requests():

    request = HttpRequest("GET", "https://www.bing.com/")
    async with AsyncioRequestsTransport() as sender:
        response = await sender.send(request)
        assert response.body() is not None

    assert isinstance(response.status_code, int)

def test_conf_async_trio_requests():

    async def do():
        request = HttpRequest("GET", "https://www.bing.com/")
        async with TrioRequestsTransport() as sender:
            return await sender.send(request)
            assert response.body() is not None

    response = trio.run(do)
    assert isinstance(response.status_code, int)


def _create_aiohttp_response(body_bytes, headers=None):
    class MockAiohttpClientResponse(aiohttp.ClientResponse):
        def __init__(self, body_bytes, headers=None):
            self._body = body_bytes
            self._headers = headers
            self._cache = {}
            self.status = 200
            self.reason = "OK"

    req_response = MockAiohttpClientResponse(body_bytes, headers)

    response = AioHttpTransportResponse(
        None, # Don't need a request here
        req_response
    )
    response._body = body_bytes

    return response


@pytest.mark.asyncio
async def test_aiohttp_response_text():

    for encoding in ["utf-8", "utf-8-sig", None]:

        res = _create_aiohttp_response(
            b'\xef\xbb\xbf56',
            {'Content-Type': 'text/plain'}
        )
        assert res.text(encoding) == '56', "Encoding {} didn't work".format(encoding)

@pytest.mark.asyncio
async def test_aiohttp_response_decompression():
    res = _create_aiohttp_response(
        b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x04\x00\x8d\x8d\xb1n\xc30\x0cD"
        b"\xff\x85s\x14HVlY\xda\x8av.\n4\x1d\x9a\x8d\xa1\xe5D\x80m\x01\x12="
        b"\x14A\xfe\xbd\x92\x81d\xceB\x1c\xef\xf8\x8e7\x08\x038\xf0\xa67Fj+"
        b"\x946\x9d8\x0c4\x08{\x96(\x94mzkh\x1cM/a\x07\x94<\xb2\x1f>\xca8\x86"
        b"\xd9\xff0\x15\xb6\x91\x8d\x12\xb2\x15\xd2\x1c\x95q\xbau\xba\xdbk"
        b"\xd5(\xd9\xb5\xa7\xc2L\x98\xf9\x8d8\xc4\xe5U\xccV,3\xf2\x9a\xcb\xddg"
        b"\xe4o\xc6T\xdeVw\x9dgL\x7f\xe0n\xc0\x91q\x02'w0b\x98JZe^\x89|\xce\x9b"
        b"\x0e\xcbW\x8a\x97\xf4X\x97\xc8\xbf\xfeYU\x1d\xc2\x85\xfc\xf4@\xb7\xbe"
        b"\xf7+&$\xf6\xa9\x8a\xcb\x96\xdc\xef\xff\xaa\xa1\x1c\xf9$\x01\x00\x00",
        {'Content-Type': 'text/plain', 'Content-Encoding':"gzip"}
    )
    body = res.body()
    expect = b'{"id":"e7877039-1376-4dcd-9b0a-192897cff780","createdDateTimeUtc":' \
             b'"2021-05-07T17:35:36.3121065Z","lastActionDateTimeUtc":' \
             b'"2021-05-07T17:35:36.3121069Z","status":"NotStarted",' \
             b'"summary":{"total":0,"failed":0,"success":0,"inProgress":0,' \
             b'"notYetStarted":0,"cancelled":0,"totalCharacterCharged":0}}'
    assert res.body() == expect, "Decompression didn't work"

@pytest.mark.asyncio
async def test_aiohttp_response_decompression_negtive():
    import zlib
    res = _create_aiohttp_response(
        b"\xff\x85s\x14HVlY\xda\x8av.\n4\x1d\x9a\x8d\xa1\xe5D\x80m\x01\x12="
        b"\x14A\xfe\xbd\x92\x81d\xceB\x1c\xef\xf8\x8e7\x08\x038\xf0\xa67Fj+"
        b"\x946\x9d8\x0c4\x08{\x96(\x94mzkh\x1cM/a\x07\x94<\xb2\x1f>\xca8\x86"
        b"\xd9\xff0\x15\xb6\x91\x8d\x12\xb2\x15\xd2\x1c\x95q\xbau\xba\xdbk"
        b"\xd5(\xd9\xb5\xa7\xc2L\x98\xf9\x8d8\xc4\xe5U\xccV,3\xf2\x9a\xcb\xddg"
        b"\xe4o\xc6T\xdeVw\x9dgL\x7f\xe0n\xc0\x91q\x02'w0b\x98JZe^\x89|\xce\x9b"
        b"\x0e\xcbW\x8a\x97\xf4X\x97\xc8\xbf\xfeYU\x1d\xc2\x85\xfc\xf4@\xb7\xbe"
        b"\xf7+&$\xf6\xa9\x8a\xcb\x96\xdc\xef\xff\xaa\xa1\x1c\xf9$\x01\x00\x00",
        {'Content-Type': 'text/plain', 'Content-Encoding':"gzip"}
    )
    with pytest.raises(zlib.error):
        body = res.body()

def test_repr():
    res = _create_aiohttp_response(
        b'\xef\xbb\xbf56',
        {}
    )
    res.content_type = "text/plain"

    assert repr(res) == "<AioHttpTransportResponse: 200 OK, Content-Type: text/plain>"