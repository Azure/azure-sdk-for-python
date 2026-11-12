# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qsl, urlsplit

import pytest
from aiohttp import web
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AioHttpTransport
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


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize(
    "status,payload,message",
    [
        (400, {}, "Unexpected response from OIDC token endpoint"),
        (200, {}, "OIDC token not found in response"),
        (200, {"value": 123}, "OIDC token not found in response"),
    ],
)
async def test_oidc_error(get_token_method, status, payload, message):
    response = mock_response(status_code=status, json_payload=payload)
    response.json = Mock(return_value=payload)
    transport = AsyncMock(send=AsyncMock(return_value=response))
    async with GitHubActionsCredential(transport=transport) as credential:
        with pytest.raises(ClientAuthenticationError, match=message) as error:
            await getattr(credential, get_token_method)("scope")
    assert error.value.response is response
    transport.send.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("use_context_manager", [False, True])
async def test_token_exchange_and_cache(get_token_method, use_context_manager):
    async def send(request, **kwargs):
        if request.method == "GET":
            assert request.headers["Authorization"] == "Bearer request-token"
            assert dict(parse_qsl(urlsplit(request.url).query)) == {
                "job": "123",
                "audience": "api://AzureADTokenExchange",
            }
            ready = asyncio.Event()
            asyncio.get_running_loop().call_soon(ready.set)
            await asyncio.wait_for(ready.wait(), timeout=1)
            response = mock_response(json_payload={"value": "github-assertion"})
            response.json = Mock(return_value={"value": "github-assertion"})
            return response
        assert request.method == "POST"
        assert request.url == "https://login.microsoftonline.com/environment-tenant/oauth2/v2.0/token"
        assert request.data["client_id"] == "environment-client"
        assert request.data["client_assertion"] == "github-assertion"
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["scope"] == "scope"
        return mock_response(json_payload=build_aad_response(access_token="azure-token"))

    transport = AsyncMock(send=AsyncMock(side_effect=send))
    credential = GitHubActionsCredential(transport=transport)

    async def get_tokens():
        for _ in range(2):
            assert (await getattr(credential, get_token_method)("scope")).token == "azure-token"

    if use_context_manager:
        async with credential:
            await get_tokens()
    else:
        try:
            await get_tokens()
        finally:
            await credential.close()
    assert transport.send.await_count == 2
    assert transport.__aexit__.await_count == 2


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
    transport = AsyncMock()
    credential = GitHubActionsCredential(transport=transport)
    async with credential as entered:
        assert entered is credential
        assert transport.__aenter__.await_count == 2
        transport.__aexit__.assert_not_awaited()
    assert transport.__aexit__.await_count == 2
    transport.__enter__.assert_not_called()
    transport.__exit__.assert_not_called()


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMock()
    credential = GitHubActionsCredential(transport=transport)
    await credential.close()
    assert transport.__aexit__.await_count == 2
    transport.__exit__.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [200, 401])
@pytest.mark.parametrize("use_custom_transport", [False, True])
async def test_real_transport_closes_after_oidc_request(status_code, use_custom_transport):
    requests = []

    async def oidc_endpoint(request):
        requests.append((request.method, request.headers.get("Authorization"), request.query.get("audience")))
        payload = {"value": "github-assertion"} if status_code == 200 else {"error": "unauthorized"}
        return web.json_response(payload, status=status_code)

    app = web.Application()
    app.router.add_get("/oidc", oidc_endpoint)
    runner = web.AppRunner(app)
    await runner.setup()
    try:
        await web.TCPSite(runner, "127.0.0.1", 0).start()
        port = runner.addresses[0][1]
        os.environ[ACTIONS_ID_TOKEN_REQUEST_URL] = f"http://127.0.0.1:{port}/oidc"
        custom_transport = AioHttpTransport() if use_custom_transport else None
        credential = GitHubActionsCredential(transport=custom_transport)
        assert isinstance(credential._pipeline, AsyncPipeline)
        transport = credential._pipeline._transport
        assert isinstance(transport, AioHttpTransport)
        if custom_transport:
            assert transport is custom_transport
        session = None

        async def authenticate():
            nonlocal session
            async with credential:
                session = transport.session
                assert session is not None
                return await credential._get_oidc_token()

        if status_code == 200:
            assert await asyncio.wait_for(authenticate(), timeout=5) == "github-assertion"
        else:
            with pytest.raises(ClientAuthenticationError) as error:
                await asyncio.wait_for(authenticate(), timeout=5)
            assert error.value.status_code == status_code
        assert requests == [("GET", "Bearer request-token", "api://AzureADTokenExchange")]
        assert session is not None and session.closed
        assert transport.session is None
    finally:
        await runner.cleanup()
