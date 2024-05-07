# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore teamprojectid, planid, jobid, oidctoken
import os
from unittest.mock import AsyncMock, patch

import pytest
from azure.identity import CredentialUnavailableError
from azure.identity.aio import AzurePipelinesCredential, ChainedTokenCredential
from azure.identity._constants import EnvironmentVariables


def test_azure_pipelines_credential_initialize():
    service_connection_id = "connection-id"
    tenant_id = "tenant-id"
    client_id = "client-id"

    credential = AzurePipelinesCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
    )

    assert credential._client_id == client_id
    assert credential._tenant_id == tenant_id
    assert credential._service_connection_id == service_connection_id


@pytest.mark.asyncio
async def test_azure_pipelines_credential_context_manager():
    transport = AsyncMock()
    credential = AzurePipelinesCredential(
        client_id="client-id", tenant_id="tenant-id", service_connection_id="connection-id", transport=transport
    )

    async with credential:
        assert transport.__enter__.called
        assert not transport.__exit__.called
    assert transport.__exit__.called


@pytest.mark.asyncio
async def test_azure_pipelines_credential_missing_env_var():
    credential = AzurePipelinesCredential(
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
    )
    environment = {
        EnvironmentVariables.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI: "foo",
        EnvironmentVariables.SYSTEM_TEAMPROJECTID: "foo",
        EnvironmentVariables.SYSTEM_PLANID: "foo",
        EnvironmentVariables.SYSTEM_JOBID: "foo",
    }

    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            await credential.get_token("scope")
        assert f"Missing values for environment variables: {EnvironmentVariables.SYSTEM_ACCESSTOKEN}" in str(ex.value)


@pytest.mark.asyncio
async def test_azure_pipelines_credential_in_chain():
    mock_credential = AsyncMock()

    with patch.dict("os.environ", {}, clear=True):
        chain_credential = ChainedTokenCredential(
            AzurePipelinesCredential(
                tenant_id="tenant-id", client_id="client-id", service_connection_id="connection-id"
            ),
            mock_credential,
        )
        await chain_credential.get_token("scope")
        assert mock_credential.get_token.called


@pytest.mark.asyncio
@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
async def test_azure_pipelines_credential_authentication():
    service_connection_id = os.environ.get("AZURE_SERVICE_CONNECTION_ID", "")
    tenant_id = os.environ.get("AZURE_SERVICE_CONNECTION_TENANT_ID", "")
    client_id = os.environ.get("AZURE_SERVICE_CONNECTION_CLIENT_ID", "")

    scope = "https://vault.azure.net/.default"

    if not all([service_connection_id, tenant_id, client_id]):
        pytest.skip("This test requires environment variables to be set")

    credential = AzurePipelinesCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        service_connection_id=service_connection_id,
    )

    token = await credential.get_token(scope)
    assert token.token
    assert isinstance(token.expires_on, int)
