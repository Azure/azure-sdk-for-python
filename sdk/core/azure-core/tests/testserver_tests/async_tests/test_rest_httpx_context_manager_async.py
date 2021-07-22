# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError, ResponseNotReadError
import pytest
from azure.core.rest import HttpRequest
from rest_client_async import AsyncTestRestClient

@pytest.mark.asyncio
async def test_normal_call(httpx_client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="/basic/string")
    response = await httpx_client.send_request(request)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with httpx_client.send_request(request) as response:
        await _raise_and_get_text(response)

    response = httpx_client.send_request(request)
    async with response as response:
        await _raise_and_get_text(response)
