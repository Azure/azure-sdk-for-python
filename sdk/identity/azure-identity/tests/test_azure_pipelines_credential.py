# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore teamprojectid, planid, jobid, oidctoken
import os
from unittest.mock import MagicMock, patch

import pytest
from azure.core.rest import HttpRequest
from azure.identity import AzurePipelinesCredential, ChainedTokenCredential, CredentialUnavailableError
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.azure_pipelines import build_oidc_request, OIDC_API_VERSION


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


def test_azure_pipelines_credential_context_manager():
    transport = MagicMock()
    credential = AzurePipelinesCredential(
        client_id="client-id", tenant_id="tenant-id", service_connection_id="connection-id", transport=transport
    )

    with credential:
        assert transport.__enter__.called
        assert not transport.__exit__.called
    assert transport.__exit__.called


def test_build_oidc_request():
    service_connection_id = "connection-id"
    collection_uri = "https://example.com"
    project_id = "team-project-id"
    plan_id = "plan-id"
    job_id = "job-id"
    access_token = "access-token"

    environment = {
        EnvironmentVariables.SYSTEM_TEAMFOUNDATIONCOLLECTIONURI: collection_uri,
        EnvironmentVariables.SYSTEM_TEAMPROJECTID: project_id,
        EnvironmentVariables.SYSTEM_PLANID: plan_id,
        EnvironmentVariables.SYSTEM_JOBID: job_id,
        EnvironmentVariables.SYSTEM_ACCESSTOKEN: access_token,
    }

    with patch.dict("os.environ", environment, clear=True):
        request: HttpRequest = build_oidc_request(service_connection_id)
        assert request.method == "POST"
        assert request.url.startswith(
            f"{collection_uri}/{project_id}/_apis/distributedtask/hubs/build/plans/{plan_id}/jobs/{job_id}/oidctoken"
        )
        assert f"api-version={OIDC_API_VERSION}" in request.url
        assert f"serviceConnectionId={service_connection_id}" in request.url
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Authorization"] == f"Bearer {access_token}"


def test_azure_pipelines_credential_missing_env_var():
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
            credential.get_token("scope")
        assert f"Missing values for environment variables: {EnvironmentVariables.SYSTEM_ACCESSTOKEN}" in str(ex.value)


def test_azure_pipelines_credential_in_chain():
    mock_credential = MagicMock()

    with patch.dict("os.environ", {}, clear=True):
        chain_credential = ChainedTokenCredential(
            AzurePipelinesCredential(
                tenant_id="tenant-id", client_id="client-id", service_connection_id="connection-id"
            ),
            mock_credential,
        )
        chain_credential.get_token("scope")
        assert mock_credential.get_token.called


@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
def test_azure_pipelines_credential_authentication():
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

    token = credential.get_token(scope)
    assert token.token
    assert isinstance(token.expires_on, int)
