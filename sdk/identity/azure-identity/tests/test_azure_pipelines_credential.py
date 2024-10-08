# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore oidcrequesturi
import os
from unittest.mock import MagicMock, patch

import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    AzurePipelinesCredential,
    ChainedTokenCredential,
    ClientAssertionCredential,
    CredentialUnavailableError,
)
from azure.identity._credentials.azure_pipelines import SYSTEM_OIDCREQUESTURI, OIDC_API_VERSION, build_oidc_request

from helpers import GET_TOKEN_METHODS


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


def test_azure_pipelines_credential_initialize_empty_kwarg():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError):
            AzurePipelinesCredential(
                system_access_token="token", client_id="client-id", tenant_id="tenant-id", service_connection_id=""
            )


def test_azure_pipelines_credential_context_manager():
    transport = MagicMock()
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
        transport=transport,
    )

    with credential:
        assert transport.__enter__.called
        assert not transport.__exit__.called
    assert transport.__exit__.called


def test_build_oidc_request():
    service_connection_id = "connection-id"
    collection_uri = "https://example.com"
    access_token = "access-token"

    environment = {SYSTEM_OIDCREQUESTURI: collection_uri}

    with patch.dict("os.environ", environment, clear=True):
        request: HttpRequest = build_oidc_request(service_connection_id, access_token)
        assert request.method == "POST"
        assert request.url.startswith(collection_uri)
        assert f"api-version={OIDC_API_VERSION}" in request.url
        assert f"serviceConnectionId={service_connection_id}" in request.url
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Authorization"] == f"Bearer {access_token}"


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_azure_pipelines_credential_missing_system_env_var(get_token_method):
    credential = AzurePipelinesCredential(
        system_access_token="token",
        client_id="client-id",
        tenant_id="tenant-id",
        service_connection_id="connection-id",
    )

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            getattr(credential, get_token_method)("scope")
        assert f"Missing value for the {SYSTEM_OIDCREQUESTURI} environment variable" in str(ex.value)


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_azure_pipelines_credential_in_chain(get_token_method):
    mock_credential = MagicMock()

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
        getattr(chain_credential, get_token_method)("scope")
        assert getattr(mock_credential, get_token_method).called


@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_azure_pipelines_credential_authentication(get_token_method):
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

    token = getattr(credential, get_token_method)(scope)
    assert token.token
    assert isinstance(token.expires_on, int)


@pytest.mark.live_test_only("Requires Azure Pipelines environment with configured service connection")
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_azure_pipelines_credential_authentication_invalid_token(get_token_method):
    system_access_token = "invalid"
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

    with pytest.raises(ClientAuthenticationError) as ex:
        getattr(credential, get_token_method)(scope)

    assert ex.value.status_code == 401
