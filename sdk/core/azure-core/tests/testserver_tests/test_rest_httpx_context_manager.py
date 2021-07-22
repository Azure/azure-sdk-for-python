# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import ResponseNotReadError

def test_normal_call(httpx_client, port):
    def _raise_and_get_text(response):
        response.raise_for_status()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="/basic/string")
    response = httpx_client.send_request(request)
    _raise_and_get_text(response)
    assert response.is_closed

    with httpx_client.send_request(request) as response:
        _raise_and_get_text(response)

    response = httpx_client.send_request(request)
    with response as response:
        _raise_and_get_text(response)
