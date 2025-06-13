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

from azure.communication.identity._shared.token_exchange_async import (
    TokenExchangeClient
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


@pytest.mark.asyncio
class TestTokenExchangeClient:
    async def test_async_exchange_entra_token_success(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse()
        client._pipeline = AsyncMock()
        client._pipeline.run.return_value = dummy_response

        token = await client.exchange_entra_token()
        assert isinstance(token, AccessToken)
        assert token.token == "tok"

    async def test_async_exchange_entra_token_failure(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(status_code=400)
        client._pipeline = AsyncMock()
        client._pipeline.run.return_value = dummy_response

        with pytest.raises(HttpResponseError):
            await client.exchange_entra_token()

    async def test_async_parse_access_token_from_response_invalid_json(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content="not json")
        with pytest.raises(ClientAuthenticationError):
            await client._parse_access_token_from_response(dummy_response)

    async def test_async_parse_access_token_from_response_missing_fields(self):
        client = TokenExchangeClient("https://endpoint", MagicMock())
        dummy_response = DummyPipelineResponse(content='{"invalid": "data"}')
        with pytest.raises(ClientAuthenticationError):
            await client._parse_access_token_from_response(dummy_response)
