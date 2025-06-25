# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest import TestCase
from unittest.mock import MagicMock, AsyncMock
from azure.communication.identity._shared.entra_token_guard_policy_async import (
    EntraTokenGuardPolicy,
)


class DummyHttpResponse:
    def __init__(self, status_code=200, expires_on=None):
        self.status_code = status_code
        self._expires_on = expires_on

    def text(self):
        if self._expires_on:
            return '{"accessToken": {"expiresOn": "%s"}}' % self._expires_on
        return '{}'


class DummyPipelineResponse:
    def __init__(self, status_code=200, expires_on=None):
        self.http_response = DummyHttpResponse(status_code, expires_on)


class DummyRequest:
    def __init__(self, token):
        self.http_request = MagicMock()
        self.http_request.headers = {"Authorization": token}


@pytest.mark.asyncio
class TestEntraTokenGuardPolicy(TestCase):
    async def test_send_cache_miss(self):
        policy = EntraTokenGuardPolicy()
        policy.next = AsyncMock()
        expires_on = "2999-12-31T23:59:59Z"
        policy.next.send.return_value = DummyPipelineResponse(200, expires_on)
        request = DummyRequest("token1")

        response = await policy.send(request)
        assert response.http_response.status_code == 200
        assert policy._entra_token_cache == "token1"
        assert policy._response_cache is response

    async def test_send_cache_hit(self):
        policy = EntraTokenGuardPolicy()
        expires_on = "2999-12-31T23:59:59Z"
        policy._entra_token_cache = "token1"
        policy._response_cache = DummyPipelineResponse(200, expires_on)
        request = DummyRequest("token1")

        response = await policy.send(request)
        assert response is policy._response_cache

    async def test_send_invalid_response_raises(self):
        policy = EntraTokenGuardPolicy()
        policy.next = AsyncMock()
        policy.next.send.return_value = None
        request = DummyRequest("token1")

        with pytest.raises(RuntimeError):
            await policy.send(request)