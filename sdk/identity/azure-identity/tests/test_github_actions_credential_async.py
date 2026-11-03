# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qsl, urlsplit

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import CredentialUnavailableError
from azure.identity._credentials.github_actions import ACTIONS_ID_TOKEN_REQUEST_URL, ACTIONS_ID_TOKEN_REQUEST_TOKEN
from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION
from azure.identity.aio import ChainedTokenCredential, GitHubActionsCredential

from helpers import GET_TOKEN_METHODS, build_aad_response, mock_response


@pytest.fixture(autouse=True)
def github_environment():
    with patch.dict(
        os.environ,
        {
            "AZURE_TENANT_ID": "environment-tenant",
            "AZURE_CLIENT_ID": "environment-client",
            ACTIONS_ID_TOKEN_REQUEST_URL: "https://example.test/oidc?job=123",
            ACTIONS_ID_TOKEN_REQUEST_TOKEN: "request-token",
        },
        clear=True,
    ):
        yield


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("missing", [ACTIONS_ID_TOKEN_REQUEST_URL, ACTIONS_ID_TOKEN_REQUEST_TOKEN])
async def test_missing_github_environment(get_token_method, missing):
    credential = GitHubActionsCredential()
    os.environ.pop(missing)
    credential._client_assertion_credential = AsyncMock()
    with pytest.raises(CredentialUnavailableError, match=missing):
        await getattr(credential, get_token_method)("scope")
    getattr(credential._client_assertion_credential, get_token_method).assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_delegation(get_token_method):
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = AsyncMock()
    expected = (
        AccessToken("access-token", 123) if get_token_method == "get_token" else AccessTokenInfo("access-token", 123)
    )
    method = getattr(credential._client_assertion_credential, get_token_method)
    method.return_value = expected
    options = {"claims": "claims", "tenant_id": "other-tenant", "enable_cae": True}
    kwargs = options if get_token_method == "get_token" else {"options": options}
    assert await getattr(credential, get_token_method)("scope", **kwargs) is expected
    method.assert_awaited_once_with("scope", **kwargs)


@pytest.mark.parametrize("status,payload", [(400, {}), (200, {}), (200, {"value": 123})])
def test_oidc_error(status, payload):
    credential = GitHubActionsCredential()
    response = Mock(status_code=status, headers={}, json=Mock(return_value=payload))
    credential._pipeline = Mock()
    credential._pipeline.run.return_value.http_response = response
    with pytest.raises(ClientAuthenticationError) as error:
        credential._get_oidc_token()
    assert error.value.response is response


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_token_exchange_and_cache(get_token_method):
    async def send(request, **kwargs):
        assert request.url == "https://login.microsoftonline.com/environment-tenant/oauth2/v2.0/token"
        assert request.data["client_id"] == "environment-client"
        assert request.data["client_assertion"] == "github-assertion"
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["scope"] == "scope"
        return mock_response(json_payload=build_aad_response(access_token="azure-token"))

    transport = Mock(send=AsyncMock(side_effect=send))
    credential = GitHubActionsCredential(transport=transport)
    credential._pipeline = Mock()
    credential._pipeline.run.return_value.http_response = Mock(
        status_code=200, json=Mock(return_value={"value": "github-assertion"})
    )
    for _ in range(2):
        assert (await getattr(credential, get_token_method)("scope")).token == "azure-token"
    transport.send.assert_awaited_once()
    credential._pipeline.run.assert_called_once()
    request = credential._pipeline.run.call_args.args[0]
    assert dict(parse_qsl(urlsplit(request.url).query))["audience"] == credential._audience


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_chain_skips_unavailable(get_token_method):
    os.environ.pop(ACTIONS_ID_TOKEN_REQUEST_URL)
    fallback = AsyncMock()
    chain = ChainedTokenCredential(GitHubActionsCredential(), fallback)
    await getattr(chain, get_token_method)("scope")
    getattr(fallback, get_token_method).assert_awaited_once()


@pytest.mark.asyncio
async def test_context_manager():
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = AsyncMock()
    credential._pipeline = Mock(__enter__=Mock(), __exit__=Mock())
    async with credential as entered:
        assert entered is credential
        credential._client_assertion_credential.__aenter__.assert_awaited_once()
        credential._pipeline.__enter__.assert_called_once()
    credential._client_assertion_credential.close.assert_awaited_once()
    credential._pipeline.__exit__.assert_called_once()


@pytest.mark.asyncio
async def test_close():
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = AsyncMock()
    credential._pipeline = Mock(__exit__=Mock())
    await credential.close()
    credential._client_assertion_credential.close.assert_awaited_once()
    credential._pipeline.__exit__.assert_called_once()
