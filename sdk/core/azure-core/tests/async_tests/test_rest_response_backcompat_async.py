# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import AioHttpTransport, AsyncioRequestsTransport, TrioRequestsTransport
from rest_client_async import AsyncTestRestClient

TRANSPORTS = [AioHttpTransport, AsyncioRequestsTransport]

@pytest.fixture

def old_request(port):
    return PipelineTransportHttpRequest("GET", "http://localhost:{}/streams/basic".format(port))

@pytest.fixture
@pytest.mark.asyncio
async def get_old_response(old_request):
    async def _callback(transport, **kwargs):
        async with transport() as sender:
            return await sender.send(old_request, **kwargs)
    return _callback

@pytest.fixture
@pytest.mark.trio
async def get_old_response_trio(old_request):
    async def _callback(**kwargs):
        async with TrioRequestsTransport() as sender:
            return await sender.send(old_request, **kwargs)
    return _callback

@pytest.fixture
def new_request(port):
    return RestHttpRequest("GET", "http://localhost:{}/streams/basic".format(port))

@pytest.fixture
@pytest.mark.asyncio
async def get_new_response(new_request):
    async def _callback(transport, **kwargs):
        async with transport() as sender:
            return await sender.send(new_request, **kwargs)
    return _callback

@pytest.fixture
@pytest.mark.trio
async def get_new_response_trio(new_request):
    async def _callback(**kwargs):
        async with TrioRequestsTransport() as sender:
            return await sender.send(new_request, **kwargs)
    return _callback

def _test_response_attr_parity(old_response, new_response):
    for attr in dir(old_response):
        if not attr[0] == "_":
            # if not a private attr, we want partiy
            assert hasattr(new_response, attr)

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_attr_parity(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_attr_parity(old_response, new_response)

@pytest.mark.trio
async def test_response_attr_parity_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_attr_parity(old_response, new_response)

def _test_response_set_attrs(old_response, new_response):
    for attr in dir(old_response):
        if attr[0] == "_":
            continue
        try:
            # if we can set it on the old request, we want to
            # be able to set it on the new
            setattr(old_response, attr, "foo")
        except:
            pass
        else:
            setattr(new_response, attr, "foo")
            assert getattr(old_response, attr) == getattr(new_response, attr) == "foo"

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_set_attrs(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_set_attrs(old_response, new_response)

@pytest.mark.trio
async def test_response_set_attrs_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_set_attrs(old_response, new_response)

def _test_response_block_size(old_response, new_response):
    assert old_response.block_size == new_response.block_size == 4096
    old_response.block_size = 500
    new_response.block_size = 500
    assert old_response.block_size == new_response.block_size == 500

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_block_size(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_block_size(old_response, new_response)

@pytest.mark.trio
async def test_response_block_size_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_block_size(old_response, new_response)

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_body(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    assert old_response.body() == new_response.body() == b"Hello, world!"

@pytest.mark.trio
async def test_response_body_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    assert old_response.body() == new_response.body() == b"Hello, world!"

def _test_response_internal_response(old_response, new_response, port):
    assert str(old_response.internal_response.url) == str(new_response.internal_response.url) == "http://localhost:{}/streams/basic".format(port)
    old_response.internal_response = "foo"
    new_response.internal_response = "foo"
    assert old_response.internal_response == new_response.internal_response == "foo"

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_internal_response(get_old_response, get_new_response, transport, port):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_internal_response(old_response, new_response, port)

@pytest.mark.trio
async def test_response_internal_response_trio(get_old_response_trio, get_new_response_trio, port):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_internal_response(old_response, new_response, port)

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_stream_download(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport, stream=True)
    new_response = await get_new_response(transport, stream=True)
    pipeline = Pipeline(transport())
    old_string = b"".join([part async for part in old_response.stream_download(pipeline=pipeline)])
    new_string = b"".join([part async for part in new_response.stream_download(pipeline=pipeline)])

    # aiohttp can be flaky for both old and new responses, so since we're just checking backcompat here
    # using in instead of equals
    assert old_string in b"Hello, world!"
    assert new_string in b"Hello, world!"

@pytest.mark.trio
async def test_response_stream_download_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio(stream=True)
    new_response = await get_new_response_trio(stream=True)
    pipeline = Pipeline(TrioRequestsTransport())
    old_string = b"".join([part async for part in old_response.stream_download(pipeline=pipeline)])
    new_string = b"".join([part async for part in new_response.stream_download(pipeline=pipeline)])
    assert old_string == new_string == b"Hello, world!"

def _test_response_request(old_response, new_response, port):
    assert old_response.request.url == new_response.request.url == "http://localhost:{}/streams/basic".format(port)
    old_response.request = "foo"
    new_response.request = "foo"
    assert old_response.request == new_response.request == "foo"

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_request(get_old_response, get_new_response, port, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_request(old_response, new_response, port)

@pytest.mark.trio
async def test_response_request_trio(get_old_response_trio, get_new_response_trio, port):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_request(old_response, new_response, port)

def _test_response_status_code(old_response, new_response):
    assert old_response.status_code == new_response.status_code == 200
    old_response.status_code = 202
    new_response.status_code = 202
    assert old_response.status_code == new_response.status_code == 202

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_status_code(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_status_code(old_response, new_response)

@pytest.mark.trio
async def test_response_status_code_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_status_code(old_response, new_response)

def _test_response_headers(old_response, new_response):
    assert set(old_response.headers.keys()) == set(new_response.headers.keys()) == set(["Content-Type", "Connection", "Server", "Date"])
    old_response.headers = {"Hello": "world!"}
    new_response.headers = {"Hello": "world!"}
    assert old_response.headers == new_response.headers == {"Hello": "world!"}

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_headers(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_headers(old_response, new_response)

@pytest.mark.trio
async def test_response_headers_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_headers(old_response, new_response)

def _test_response_reason(old_response, new_response):
    assert old_response.reason == new_response.reason == "OK"
    old_response.reason = "Not OK"
    new_response.reason = "Not OK"
    assert old_response.reason == new_response.reason == "Not OK"

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_reason(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_reason(old_response, new_response)

@pytest.mark.trio
async def test_response_reason_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_reason(old_response, new_response)

def _test_response_content_type(old_response, new_response):
    assert old_response.content_type == new_response.content_type == "text/html; charset=utf-8"
    old_response.content_type = "application/json"
    new_response.content_type = "application/json"
    assert old_response.content_type == new_response.content_type == "application/json"

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_content_type(get_old_response, get_new_response, transport):
    old_response = await get_old_response(transport)
    new_response = await get_new_response(transport)
    _test_response_content_type(old_response, new_response)

@pytest.mark.trio
async def test_response_content_type_trio(get_old_response_trio, get_new_response_trio):
    old_response = await get_old_response_trio()
    new_response = await get_new_response_trio()
    _test_response_content_type(old_response, new_response)

def _create_multiapart_request(http_request_class):
    class ResponsePolicy(object):
        def on_request(self, *args):
            return

        def on_response(self, request, response):
            response.http_response.headers['x-ms-fun'] = 'true'

    class AsyncResponsePolicy(object):
        def on_request(self, *args):
            return

        async def on_response(self, request, response):
            response.http_response.headers['x-ms-async-fun'] = 'true'

    req0 = http_request_class("DELETE", "/container0/blob0")
    req1 = http_request_class("DELETE", "/container1/blob1")
    request = http_request_class("POST", "/multipart/request")
    request.set_multipart_mixed(req0, req1, policies=[ResponsePolicy(), AsyncResponsePolicy()])
    return request

async def _test_parts(response):
    # hack the content type
    parts = [p async for p in response.parts()]
    assert len(parts) == 2

    parts0 = parts[0]
    assert parts0.status_code == 202
    assert parts0.headers['x-ms-fun'] == 'true'
    assert parts0.headers['x-ms-async-fun'] == 'true'

    parts1 = parts[1]
    assert parts1.status_code == 404
    assert parts1.headers['x-ms-fun'] == 'true'
    assert parts1.headers['x-ms-async-fun'] == 'true'

@pytest.mark.asyncio
@pytest.mark.parametrize("transport", TRANSPORTS)
async def test_response_parts(port, transport):
    # there's no support for trio + multipart rn
    old_request = _create_multiapart_request(PipelineTransportHttpRequest)
    new_request = _create_multiapart_request(RestHttpRequest)
    old_response = await AsyncTestRestClient(port, transport=transport()).send_request(old_request, stream=True)
    new_response = await AsyncTestRestClient(port, transport=transport()).send_request(new_request, stream=True)
    if hasattr(old_response, "load_body"):
        # only aiohttp has this attr
        await old_response.load_body()
        await new_response.load_body()
    await _test_parts(old_response)
    await _test_parts(new_response)
