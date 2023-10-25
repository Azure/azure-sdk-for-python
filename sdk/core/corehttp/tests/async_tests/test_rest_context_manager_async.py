# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.exceptions import ResponseNotReadError
from corehttp.rest import HttpRequest


@pytest.mark.asyncio
async def test_normal_call(client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = HttpRequest("GET", url="/basic/string")
    response = await client.send_request(request)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with client.send_request(request) as response:
        await _raise_and_get_text(response)

    response = client.send_request(request)
    async with response as response:
        await _raise_and_get_text(response)


@pytest.mark.asyncio
async def test_stream_call(client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        assert not response.is_closed
        with pytest.raises(ResponseNotReadError):
            response.text()
        await response.read()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = HttpRequest("GET", url="/streams/basic")
    response = await client.send_request(request, stream=True)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with client.send_request(request, stream=True) as response:
        await _raise_and_get_text(response)
    assert response.is_closed

    response = client.send_request(request, stream=True)
    async with response as response:
        await _raise_and_get_text(response)
