# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import TrioRequestsTransport, HttpRequest, TrioRequestsTransportResponse

import pytest
import requests
import json


@pytest.mark.trio
async def test_async_gen_data():
    class AsyncGen:
        def __init__(self):
            self._range = iter([b"azerty"])

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._range)
            except StopIteration:
                raise StopAsyncIteration

    async with TrioRequestsTransport() as transport:
        req = HttpRequest('GET', 'http://httpbin.org/anything', data=AsyncGen())
        response = await transport.send(req)
        assert json.loads(response.text())['data'] == "azerty"

@pytest.mark.trio
async def test_send_data():
    async with TrioRequestsTransport() as transport:
        req = HttpRequest('PUT', 'http://httpbin.org/anything', data=b"azerty")
        response = await transport.send(req)

        assert json.loads(response.text())['data'] == "azerty"

def _create_trio_requests_transport_response(body_bytes, headers=None):
    # https://github.com/psf/requests/blob/67a7b2e8336951d527e223429672354989384197/requests/adapters.py#L255
    req_response = requests.Response()
    req_response._content = body_bytes
    req_response._content_consumed = True
    req_response.status_code = 200
    req_response.reason = 'OK'
    if headers:
        # req_response.headers is type CaseInsensitiveDict
        req_response.headers.update(headers)
    req_response.encoding = requests.utils.get_encoding_from_headers(req_response.headers)

    response = TrioRequestsTransportResponse(
        None, # Don't need a request here
        req_response
    )

    return response

@pytest.mark.trio
def test_aiohttp_response_json():
    res = _create_trio_requests_transport_response(b'{"key": "value"}')
    assert res.json() == {"key": "value"}
    assert json.dumps(res.json())

@pytest.mark.trio
def test_aiohttp_response_json_error():
    res = _create_trio_requests_transport_response(b'this is not json serializable')
    with pytest.raises(json.decoder.JSONDecodeError):
        res.json()
