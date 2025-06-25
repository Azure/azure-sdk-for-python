# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from azure.core.exceptions import HttpResponseError

import azure.communication.identity._shared.token_utils as utils

from azure.communication.identity._shared.token_utils import (
    TEAMS_EXTENSION_SCOPE_PREFIX,
    COMMUNICATION_CLIENTS_SCOPE_PREFIX,
    TEAMS_EXTENSION_ENDPOINT,
    TEAMS_EXTENSION_API_VERSION,
    COMMUNICATION_CLIENTS_ENDPOINT,
    COMMUNICATION_CLIENTS_API_VERSION,
)


class DummyResponse:
    def __init__(self, status_code=200, expires_on=None):
        self.http_response = MagicMock()
        self.http_response.status_code = status_code
        self.http_response.text.return_value = (
            '{"accessToken": {"expiresOn": "%s"}}' % expires_on
            if expires_on else '{}'
        )


class TestTokenUtils(unittest.TestCase):
    def test_is_entra_token_cache_valid(self):
        request = MagicMock()
        request.http_request.headers = {"Authorization": "token"}
        valid, token = utils.is_entra_token_cache_valid("token", request)
        self.assertTrue(valid)
        self.assertEqual(token, "token")

        valid, token = utils.is_entra_token_cache_valid("other", request)
        self.assertFalse(valid)
        self.assertEqual(token, "token")

    def test_is_acs_token_cache_valid(self):
        # Valid response
        expires_on = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertTrue(utils.is_acs_token_cache_valid(response))

        # Expired token
        expires_on = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        response = DummyResponse(status_code=200, expires_on=expires_on)
        self.assertFalse(utils.is_acs_token_cache_valid(response))

        # Invalid response
        response = DummyResponse(status_code=400)
        self.assertFalse(utils.is_acs_token_cache_valid(response))

        # Exception in parsing
        response = DummyResponse(status_code=200)
        response.http_response.text.return_value = "not json"
        with self.assertRaises(Exception):
            utils.is_acs_token_cache_valid(response)

    def test_create_request_message_and_uri(self):
        uri = utils.create_request_uri("https://endpoint", [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert uri.startswith("https://endpoint")
        assert TEAMS_EXTENSION_ENDPOINT in uri

        req = utils.create_request_message("https://endpoint",
                                                         [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert req.method == "POST"
        assert req.headers["Accept"] == "application/json"
        assert req.headers["Content-Type"] == "application/json"

    def test_determine_endpoint_and_api_version_teams_extension(self):
        endpoint, api_version = utils.determine_endpoint_and_api_version(
            [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert endpoint == TEAMS_EXTENSION_ENDPOINT
        assert api_version == TEAMS_EXTENSION_API_VERSION

    def test_determine_endpoint_and_api_version_communication_clients(self):
        endpoint, api_version = utils.determine_endpoint_and_api_version(
            [COMMUNICATION_CLIENTS_SCOPE_PREFIX + ".default"])
        assert endpoint == COMMUNICATION_CLIENTS_ENDPOINT
        assert api_version == COMMUNICATION_CLIENTS_API_VERSION

    def test_determine_endpoint_and_api_version_invalid_scope(self):
        with pytest.raises(ValueError):
            utils.determine_endpoint_and_api_version(["invalid-scope"])

    def test_parse_expires_on_iso_string(self):
        epoch = utils.parse_expires_on("2999-12-31T23:59:59Z", MagicMock())
        assert isinstance(epoch, int)

    def test_parse_expires_on_invalid_type(self):
        with pytest.raises(HttpResponseError):
            utils.parse_expires_on(None, MagicMock())

    def test_parse_expires_on_invalid_string(self):
        with pytest.raises(HttpResponseError):
            utils.parse_expires_on("invalid-date", MagicMock())
