# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from unittest.mock import MagicMock

from azure.communication.identity._shared.token_exchange_utils import (
    TokenExchangeUtils,
    TEAMS_EXTENSION_SCOPE_PREFIX,
    COMMUNICATION_CLIENTS_SCOPE_PREFIX,
    TEAMS_EXTENSION_ENDPOINT,
    TEAMS_EXTENSION_API_VERSION,
    COMMUNICATION_CLIENTS_ENDPOINT,
    COMMUNICATION_CLIENTS_API_VERSION,
)


class TestTokenExchangeUtils:
    def test_create_request_message_and_uri(self):
        uri = TokenExchangeUtils.create_request_uri("https://endpoint", [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert uri.startswith("https://endpoint")
        assert TEAMS_EXTENSION_ENDPOINT in uri

        req = TokenExchangeUtils.create_request_message("https://endpoint",
                                                         [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert req.method == "POST"
        assert req.headers["Accept"] == "application/json"
        assert req.headers["Content-Type"] == "application/json"

    def test_determine_endpoint_and_api_version_teams_extension(self):
        endpoint, api_version = TokenExchangeUtils.determine_endpoint_and_api_version(
            [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert endpoint == TEAMS_EXTENSION_ENDPOINT
        assert api_version == TEAMS_EXTENSION_API_VERSION

    def test_determine_endpoint_and_api_version_communication_clients(self):
        endpoint, api_version = TokenExchangeUtils.determine_endpoint_and_api_version(
            [COMMUNICATION_CLIENTS_SCOPE_PREFIX + ".default"])
        assert endpoint == COMMUNICATION_CLIENTS_ENDPOINT
        assert api_version == COMMUNICATION_CLIENTS_API_VERSION

    def test_determine_endpoint_and_api_version_invalid_scope(self):
        with pytest.raises(ValueError):
            TokenExchangeUtils.determine_endpoint_and_api_version(["invalid-scope"])

    def test_parse_expires_on_iso_string(self):
        epoch = TokenExchangeUtils.parse_expires_on("2999-12-31T23:59:59Z", MagicMock())
        assert isinstance(epoch, int)

    def test_parse_expires_on_invalid_type(self):
        with pytest.raises(HttpResponseError):
            TokenExchangeUtils.parse_expires_on(None, MagicMock())

    def test_parse_expires_on_invalid_string(self):
        with pytest.raises(HttpResponseError):
            TokenExchangeUtils.parse_expires_on("invalid-date", MagicMock())

