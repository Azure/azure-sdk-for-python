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
from unittest.mock import MagicMock
from azure.communication.identity._shared.entra_token_guard_policy import (
    EntraTokenGuardPolicy
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
