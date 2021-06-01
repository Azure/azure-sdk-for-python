# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
import pytest
from azure.core.rest import HttpRequest, ResponseNotReadError

@pytest.mark.asyncio
async def test_normal_call(client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        with pytest.raises(ResponseNotReadError):
            response.text
        await response.read()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="http://localhost:5000/basic/string")
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
            response.text
        await response.read()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="http://localhost:5000/streams/basic")
    response = await client.send_request(request, stream=True)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with client.send_request(request, stream=True) as response:
        await _raise_and_get_text(response)
    assert response.is_closed

    response = client.send_request(request, stream=True)
    async with response as response:
        await _raise_and_get_text(response)

@pytest.mark.asyncio
async def test_stream_with_error(client):
    request = HttpRequest("GET", url="http://localhost:5000/streams/error")
    async with client.send_request(request, stream=True) as response:
        assert not response.is_closed
        with pytest.raises(HttpResponseError) as e:
            response.raise_for_status()
        error = e.value
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert "Operation returned an invalid status 'BAD REQUEST'" in str(error)
        with pytest.raises(ResponseNotReadError):
            error.error
        with pytest.raises(ResponseNotReadError):
            error.model
        with pytest.raises(ResponseNotReadError):
            response.json()
        with pytest.raises(ResponseNotReadError):
            response.content

        # NOW WE READ THE RESPONSE
        await response.read()
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert error.error.code == "BadRequest"
        assert error.error.message == "You made a bad request"
        assert error.model.code == "BadRequest"
        assert error.error.message == "You made a bad request"
