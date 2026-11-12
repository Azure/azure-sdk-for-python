# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore oidcrequesturi
import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AioHttpTransport
from azure.identity import CredentialUnavailableError
from azure.identity._credentials.azure_pipelines import SYSTEM_OIDCREQUESTURI
from azure.identity.aio import AzurePipelinesCredential, ChainedTokenCredential, ClientAssertionCredential

from helpers import build_aad_response, mock_response, GET_TOKEN_METHODS


def test_azure_pipelines_credential_initialize():
    system_access_token = "token"
    service_connection_id = "connection-id"
    tenant_id = "tenant-id"
    client_id = "client-id"

    credential = AzurePipelinesCredential(
        system_access_token=system_access_token,
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
    )

    assert credential._service_connection_id == service_connection_id
    assert credential._system_access_token == system_access_token
    assert isinstance(credential._client_assertion_credential, ClientAssertionCredential)
    assert isinstance(credential._pipeline, AsyncPipeline)
    assert isinstance(credential._pipeline._transport, AioHttpTransport)


@pytest.mark.asyncio
async def test_azure_pipelines_credential_initialize_empty_kwarg():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError):
            AzurePipelinesCredential(
                system_access_token="token", client_id="client-id", tenant_id="tenant-id", service_connection_id=""
            )


@pytest.mark.asyncio
async def test_azure_pipelines_credential_context_manager():
    transport = AsyncMock()
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
        transport=transport,
    )

    async with credential:
        assert transport.__aenter__.await_count == 2
        transport.__aexit__.assert_not_awaited()
    assert transport.__aexit__.await_count == 2
    transport.__enter__.assert_not_called()
    transport.__exit__.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("use_context_manager", [False, True])
async def test_azure_pipelines_credential_async_pipeline(get_token_method, use_context_manager):
    oidc_url = "https://example.com/oidc"
    assertion = "oidc-token"
    access_token = "access-token"
    oidc_response = mock_response(json_payload={"oidcToken": assertion})
    oidc_response.json.return_value = {"oidcToken": assertion}

    async def send(request, **kwargs):
        if request.url.startswith(oidc_url):
            assert request.method == "POST"
            assert request.headers["Authorization"] == "Bearer system-access-token"
            assert "serviceConnectionId=connection-id" in request.url
            ready = asyncio.Event()
            asyncio.get_running_loop().call_soon(ready.set)
            await asyncio.wait_for(ready.wait(), timeout=1)
            return oidc_response
        assert request.data["client_assertion"] == assertion
        return mock_response(json_payload=build_aad_response(access_token=access_token))

    transport = AsyncMock(send=AsyncMock(side_effect=send))
    credential = AzurePipelinesCredential(
        system_access_token="system-access-token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
        transport=transport,
    )

    with patch.dict("os.environ", {SYSTEM_OIDCREQUESTURI: oidc_url}, clear=True):
        if use_context_manager:
            async with credential:
                token = await getattr(credential, get_token_method)("scope")
        else:
            try:
                token = await getattr(credential, get_token_method)("scope")
            finally:
                await credential.close()

    assert token.token == access_token
    assert transport.send.await_count == 2
    assert transport.__aexit__.await_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize(
    "status_code, payload, message",
    [
        (401, {"error": "unauthorized"}, "Unexpected response from OIDC token endpoint"),
        (200, {}, "OIDC token not found in response"),
    ],
)
async def test_azure_pipelines_credential_oidc_error(get_token_method, status_code, payload, message):
    response = mock_response(status_code=status_code, json_payload=payload)
    response.json.return_value = payload
    transport = AsyncMock(send=AsyncMock(return_value=response))
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
        transport=transport,
    )

    with patch.dict("os.environ", {SYSTEM_OIDCREQUESTURI: "https://example.com/oidc"}, clear=True):
        async with credential:
            with pytest.raises(ClientAuthenticationError, match=message):
                await getattr(credential, get_token_method)("scope")
    transport.send.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_azure_pipelines_credential_missing_system_env_var(get_token_method):
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
    )

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            await getattr(credential, get_token_method)("scope")
        assert f"Missing value for the {SYSTEM_OIDCREQUESTURI} environment variable" in str(ex.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_azure_pipelines_credential_in_chain(get_token_method):
    mock_credential = AsyncMock()

    with patch.dict("os.environ", {}, clear=True):
        chain_credential = ChainedTokenCredential(
            AzurePipelinesCredential(
                system_access_token="token",
                tenant_id="tenant-id",
                client_id="client-id",
                service_connection_id="connection-id",
            ),
            mock_credential,
        )
        await getattr(chain_credential, get_token_method)("scope")
        assert getattr(mock_credential, get_token_method).called


@pytest.mark.asyncio
@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("use_custom_transport", [False, True])
async def test_azure_pipelines_credential_authentication(get_token_method, use_custom_transport):
    system_access_token = os.environ.get("SYSTEM_ACCESSTOKEN", "")
    service_connection_id = os.environ.get("AZURE_SERVICE_CONNECTION_ID", "")
    tenant_id = os.environ.get("AZURE_SERVICE_CONNECTION_TENANT_ID", "")
    client_id = os.environ.get("AZURE_SERVICE_CONNECTION_CLIENT_ID", "")

    scope = "https://vault.azure.net/.default"

    if not all(
        [system_access_token, os.environ.get(SYSTEM_OIDCREQUESTURI), service_connection_id, tenant_id, client_id]
    ):
        pytest.skip("This test requires Azure Pipelines OIDC and service connection environment variables")

    transport = AioHttpTransport() if use_custom_transport else None
    credential = AzurePipelinesCredential(
        system_access_token=system_access_token,
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
        transport=transport,
    )

    async with credential:
        session = transport.session if transport is not None else None
        if transport is not None:
            assert session is not None
        token = await getattr(credential, get_token_method)(scope)

    assert token.token
    assert isinstance(token.expires_on, int)
    if transport is not None:
        assert session.closed
        assert transport.session is None


@pytest.mark.asyncio
@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_azure_pipelines_credential_authentication_invalid_token(get_token_method):
    system_access_token = "invalid"
    service_connection_id = os.environ.get("AZURE_SERVICE_CONNECTION_ID", "")
    tenant_id = os.environ.get("AZURE_SERVICE_CONNECTION_TENANT_ID", "")
    client_id = os.environ.get("AZURE_SERVICE_CONNECTION_CLIENT_ID", "")

    scope = "https://vault.azure.net/.default"

    if not all([os.environ.get(SYSTEM_OIDCREQUESTURI), service_connection_id, tenant_id, client_id]):
        pytest.skip("This test requires Azure Pipelines OIDC and service connection environment variables")

    transport = AioHttpTransport()
    credential = AzurePipelinesCredential(
        system_access_token=system_access_token,
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
        transport=transport,
    )

    with pytest.raises(ClientAuthenticationError) as ex:
        async with credential:
            session = transport.session
            assert session is not None
            await getattr(credential, get_token_method)(scope)

    assert ex.value.status_code == 401
    assert session.closed
    assert transport.session is None
