# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore oidcrequesturi
import os
from unittest.mock import AsyncMock, patch

import pytest
from azure.identity import CredentialUnavailableError
from azure.identity._credentials.azure_pipelines import SYSTEM_OIDCREQUESTURI
from azure.identity.aio import AzurePipelinesCredential, ChainedTokenCredential, ClientAssertionCredential


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
        assert transport.__enter__.called
        assert not transport.__exit__.called
    assert transport.__exit__.called


@pytest.mark.asyncio
async def test_azure_pipelines_credential_missing_system_env_var():
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
    )

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            await credential.get_token("scope")
        assert f"Missing value for the {SYSTEM_OIDCREQUESTURI} environment variable" in str(ex.value)


@pytest.mark.asyncio
async def test_azure_pipelines_credential_in_chain():
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
        await chain_credential.get_token("scope")
        assert mock_credential.get_token.called


@pytest.mark.asyncio
@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
async def test_azure_pipelines_credential_authentication():
    system_access_token = os.environ.get("SYSTEM_ACCESSTOKEN", "")
    service_connection_id = os.environ.get("AZURE_SERVICE_CONNECTION_ID", "")
    tenant_id = os.environ.get("AZURE_SERVICE_CONNECTION_TENANT_ID", "")
    client_id = os.environ.get("AZURE_SERVICE_CONNECTION_CLIENT_ID", "")

    scope = "https://vault.azure.net/.default"

    if not all([service_connection_id, tenant_id, client_id]):
        pytest.skip("This test requires environment variables to be set")

    credential = AzurePipelinesCredential(
        system_access_token=system_access_token,
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
    )

    token = await credential.get_token(scope)
    assert token.token
    assert isinstance(token.expires_on, int)
