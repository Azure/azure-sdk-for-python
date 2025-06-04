# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from unittest.mock import MagicMock, AsyncMock

# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.communication.identity._shared.token_exchange import (
    TokenExchangeClient,
    AsyncTokenExchangeClient,
    _TokenExchangeUtils,
    TEAMS_EXTENSION_SCOPE_PREFIX,
    COMMUNICATION_CLIENTS_SCOPE_PREFIX,
    TEAMS_EXTENSION_ENDPOINT,
    TEAMS_EXTENSION_API_VERSION,
    COMMUNICATION_CLIENTS_ENDPOINT,
    COMMUNICATION_CLIENTS_API_VERSION,
)


class DummyPipelineResponse:
    def __init__(self, status_code=200, token="tok", expires_on="2999-12-31T23:59:59Z", content=None):
        self.http_response = MagicMock()
        self.http_response.status_code = status_code
        if content is not None:
            self.http_response.text.return_value = content
        else:
            self.http_response.text.return_value = (
                f'{{"accessToken": {{"token": "{token}", "expiresOn": "{expires_on}"}}}}'
                if status_code == 200 else '{}'
            )


class TestTokenExchangeClient:
    def test_exchange_entra_token_success(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse()
        client._pipeline = MagicMock()
        client._pipeline.run.return_value = dummy_response

        token = client.exchange_entra_token()
        assert isinstance(token, AccessToken)
        assert token.token == "tok"

    def test_exchange_entra_token_failure(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(status_code=400)
        client._pipeline = MagicMock()
        client._pipeline.run.return_value = dummy_response

        with pytest.raises(HttpResponseError):
            client.exchange_entra_token()

    def test_parse_access_token_from_response_invalid_json(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content="not json")
        with pytest.raises(ClientAuthenticationError):
            client._parse_access_token_from_response(dummy_response)

    def test_parse_access_token_from_response_missing_fields(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content='{"invalid": "data"}')
        with pytest.raises(ClientAuthenticationError):
            client._parse_access_token_from_response(dummy_response)


@pytest.mark.asyncio
class TestAsyncTokenExchangeClient:
    async def test_async_exchange_entra_token_success(self):
        client = AsyncTokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse()
        client._pipeline = AsyncMock()
        client._pipeline.run.return_value = dummy_response

        token = await client.exchange_entra_token()
        assert isinstance(token, AccessToken)
        assert token.token == "tok"

    async def test_async_exchange_entra_token_failure(self):
        client = AsyncTokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(status_code=400)
        client._pipeline = AsyncMock()
        client._pipeline.run.return_value = dummy_response

        with pytest.raises(HttpResponseError):
            await client.exchange_entra_token()

    async def test_async_parse_access_token_from_response_invalid_json(self):
        client = AsyncTokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content="not json")
        with pytest.raises(ClientAuthenticationError):
            await client._parse_access_token_from_response(dummy_response)

    async def test_async_parse_access_token_from_response_missing_fields(self):
        client = AsyncTokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content='{"invalid": "data"}')
        with pytest.raises(ClientAuthenticationError):
            await client._parse_access_token_from_response(dummy_response)


class TestTokenExchangeUtils:
    def test_create_request_message_and_uri(self):
        uri = _TokenExchangeUtils.create_request_uri("https://endpoint", [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert uri.startswith("https://endpoint")
        assert TEAMS_EXTENSION_ENDPOINT in uri

        req = _TokenExchangeUtils.create_request_message("https://endpoint",
                                                         [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert req.method == "POST"
        assert req.headers["Accept"] == "application/json"
        assert req.headers["Content-Type"] == "application/json"

    def test_determine_endpoint_and_api_version_teams_extension(self):
        endpoint, api_version = _TokenExchangeUtils.determine_endpoint_and_api_version(
            [TEAMS_EXTENSION_SCOPE_PREFIX + ".default"])
        assert endpoint == TEAMS_EXTENSION_ENDPOINT
        assert api_version == TEAMS_EXTENSION_API_VERSION

    def test_determine_endpoint_and_api_version_communication_clients(self):
        endpoint, api_version = _TokenExchangeUtils.determine_endpoint_and_api_version(
            [COMMUNICATION_CLIENTS_SCOPE_PREFIX + ".default"])
        assert endpoint == COMMUNICATION_CLIENTS_ENDPOINT
        assert api_version == COMMUNICATION_CLIENTS_API_VERSION

    def test_determine_endpoint_and_api_version_invalid_scope(self):
        with pytest.raises(ValueError):
            _TokenExchangeUtils.determine_endpoint_and_api_version(["invalid-scope"])

    def test_parse_expires_on_iso_string(self):
        epoch = _TokenExchangeUtils.parse_expires_on("2999-12-31T23:59:59Z", MagicMock())
        assert isinstance(epoch, int)

    def test_parse_expires_on_invalid_type(self):
        with pytest.raises(HttpResponseError):
            _TokenExchangeUtils.parse_expires_on(None, MagicMock())

    def test_parse_expires_on_invalid_string(self):
        with pytest.raises(ValueError):
            _TokenExchangeUtils.parse_expires_on("invalid-date", MagicMock())

