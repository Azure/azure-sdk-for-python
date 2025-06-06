# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta, timezone
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import HttpRequest

import pytest
from unittest import TestCase
from unittest.mock import MagicMock, AsyncMock


from azure.communication.identity._shared.entra_token_guard_policy import (
    EntraTokenGuardPolicy,
    AsyncEntraTokenGuardPolicy,
    _EntraTokenGuardUtils,
)

class DummyResponse:
    def __init__(self, status_code=200, expires_on=None):
        self.http_response = MagicMock()
        self.http_response.status_code = status_code
        self.http_response.text.return_value = (
            '{"accessToken": {"expiresOn": "%s"}}' % expires_on
            if expires_on else '{}'
        )

class TestEntraTokenGuardPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = EntraTokenGuardPolicy()
        self.policy.next = MagicMock()
        self.request = PipelineRequest(HttpRequest("GET", "http://test"), None)

    def test_send_cache_miss(self):
        self.policy.next.send.return_value = DummyResponse(
            status_code=200,
            expires_on=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        )
        self.request.http_request.headers["Authorization"] = "token"
        response = self.policy.send(self.request)
        self.assertIsNotNone(response)
        self.assertEqual(response.http_response.status_code, 200)

    def test_send_cache_hit(self):
        # Simulate a valid cache
        self.policy._entra_token_cache = "token"
        self.policy._response_cache = DummyResponse(
            status_code=200,
            expires_on=(datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        )
        self.request.http_request.headers["Authorization"] = "token"
        response = self.policy.send(self.request)
        self.assertIsNotNone(response)
        self.assertEqual(response.http_response.status_code, 200)

    def test_send_invalid_response(self):
        self.policy.next.send.return_value = None
        self.request.http_request.headers["Authorization"] = "token"
        with self.assertRaises(RuntimeError):
            self.policy.send(self.request)

class TestEntraTokenGuardUtils(unittest.TestCase):
    def test_is_entra_token_cache_valid(self):
        request = MagicMock()
        request.http_request.headers = {"Authorization": "token"}
        valid, token = _EntraTokenGuardUtils.is_entra_token_cache_valid("token", request)
        self.assertTrue(valid)
        self.assertEqual(token, "token")

        valid, token = _EntraTokenGuardUtils.is_entra_token_cache_valid("other", request)
        self.assertFalse(valid)
        self.assertEqual(token, "token")

    def test_is_acs_token_cache_valid(self):
        # Valid response
        expires_on = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertTrue(_EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Expired token
        expires_on = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertFalse(_EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Invalid response
        response = DummyResponse(status_code=400)
        self.assertFalse(_EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Exception in parsing
        response = DummyResponse(status_code=200)
        response.http_response.text.return_value = "not json"
        self.assertFalse(_EntraTokenGuardUtils.is_acs_token_cache_valid(response))

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
class TestAsyncEntraTokenGuardPolicy(TestCase):
    async def test_send_cache_miss(self):
        policy = AsyncEntraTokenGuardPolicy()
        policy.next = AsyncMock()
        expires_on = "2999-12-31T23:59:59Z"
        policy.next.send.return_value = DummyPipelineResponse(200, expires_on)
        request = DummyRequest("token1")

        response = await policy.send(request)
        assert response.http_response.status_code == 200
        assert policy._entra_token_cache == "token1"
        assert policy._response_cache is response

    async def test_send_cache_hit(self):
        policy = AsyncEntraTokenGuardPolicy()
        expires_on = "2999-12-31T23:59:59Z"
        policy._entra_token_cache = "token1"
        policy._response_cache = DummyPipelineResponse(200, expires_on)
        request = DummyRequest("token1")

        response = await policy.send(request)
        assert response is policy._response_cache

    async def test_send_invalid_response_raises(self):
        policy = AsyncEntraTokenGuardPolicy()
        policy.next = AsyncMock()
        policy.next.send.return_value = None
        request = DummyRequest("token1")

        with pytest.raises(RuntimeError):
            await policy.send(request)