# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, AsyncMock
from azure.communication.identity._shared.entra_token_guard_policy_utils import (
    EntraTokenGuardUtils,
)

class DummyResponse:
    def __init__(self, status_code=200, expires_on=None):
        self.http_response = MagicMock()
        self.http_response.status_code = status_code
        self.http_response.text.return_value = (
            '{"accessToken": {"expiresOn": "%s"}}' % expires_on
            if expires_on else '{}'
        )


class TestEntraTokenGuardUtils(unittest.TestCase):
    def test_is_entra_token_cache_valid(self):
        request = MagicMock()
        request.http_request.headers = {"Authorization": "token"}
        valid, token = EntraTokenGuardUtils.is_entra_token_cache_valid("token", request)
        self.assertTrue(valid)
        self.assertEqual(token, "token")

        valid, token = EntraTokenGuardUtils.is_entra_token_cache_valid("other", request)
        self.assertFalse(valid)
        self.assertEqual(token, "token")

    def test_is_acs_token_cache_valid(self):
        # Valid response
        expires_on = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertTrue(EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Expired token
        expires_on = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertFalse(EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Invalid response
        response = DummyResponse(status_code=400)
        self.assertFalse(EntraTokenGuardUtils.is_acs_token_cache_valid(response))

        # Exception in parsing
        response = DummyResponse(status_code=200)
        response.http_response.text.return_value = "not json"
        self.assertFalse(EntraTokenGuardUtils.is_acs_token_cache_valid(response))

