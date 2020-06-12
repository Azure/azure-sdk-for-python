# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import itertools
import os
from unittest import mock

from azure.identity import CredentialUnavailableError
from azure.identity.aio import EnvironmentCredential
from azure.identity._constants import EnvironmentVariables
import pytest

from helpers import mock_response, Request
from helpers_async import async_validating_transport
from test_environment_credential import ALL_VARIABLES


@pytest.mark.asyncio
async def test_incomplete_configuration():
    """get_token should raise CredentialUnavailableError for incomplete configuration."""

    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(CredentialUnavailableError) as ex:
            await EnvironmentCredential().get_token("scope")

    for a, b in itertools.combinations(ALL_VARIABLES, 2):  # all credentials require at least 3 variables set
        with mock.patch.dict(os.environ, {a: "a", b: "b"}, clear=True):
            with pytest.raises(CredentialUnavailableError) as ex:
                await EnvironmentCredential().get_token("scope")


@pytest.mark.parametrize(
    "credential_name,environment_variables",
    (
        ("ClientSecretCredential", EnvironmentVariables.CLIENT_SECRET_VARS),
        ("CertificateCredential", EnvironmentVariables.CERT_VARS),
    ),
)
def test_passes_authority_argument(credential_name, environment_variables):
    """the credential pass the 'authority' keyword argument to its inner credential"""

    authority = "authority"

    with mock.patch.dict("os.environ", {variable: "foo" for variable in environment_variables}, clear=True):
        with mock.patch(EnvironmentCredential.__module__ + "." + credential_name) as mock_credential:
            EnvironmentCredential(authority=authority)

    assert mock_credential.call_count == 1
    _, kwargs = mock_credential.call_args
    assert kwargs["authority"] == authority


def test_client_secret_configuration():
    """the credential should pass expected values and any keyword arguments to its inner credential"""

    client_id = "client-id"
    client_secret = "..."
    tenant_id = "tenant_id"
    bar = "bar"

    environment = {
        EnvironmentVariables.AZURE_CLIENT_ID: client_id,
        EnvironmentVariables.AZURE_CLIENT_SECRET: client_secret,
        EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
    }
    with mock.patch(EnvironmentCredential.__module__ + ".ClientSecretCredential") as mock_credential:
        with mock.patch.dict("os.environ", environment, clear=True):
            EnvironmentCredential(foo=bar)

    assert mock_credential.call_count == 1
    _, kwargs = mock_credential.call_args
    assert kwargs["client_id"] == client_id
    assert kwargs["client_secret"] == client_secret
    assert kwargs["tenant_id"] == tenant_id
    assert kwargs["foo"] == bar


def test_certificate_configuration():
    """the credential should pass expected values and any keyword arguments to its inner credential"""

    client_id = "client-id"
    certificate_path = "..."
    tenant_id = "tenant_id"
    bar = "bar"

    environment = {
        EnvironmentVariables.AZURE_CLIENT_ID: client_id,
        EnvironmentVariables.AZURE_CLIENT_CERTIFICATE_PATH: certificate_path,
        EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
    }
    with mock.patch(EnvironmentCredential.__module__ + ".CertificateCredential") as mock_credential:
        with mock.patch.dict("os.environ", environment, clear=True):
            EnvironmentCredential(foo=bar)

    assert mock_credential.call_count == 1
    _, kwargs = mock_credential.call_args
    assert kwargs["client_id"] == client_id
    assert kwargs["certificate_path"] == certificate_path
    assert kwargs["tenant_id"] == tenant_id
    assert kwargs["foo"] == bar


@pytest.mark.asyncio
async def test_client_secret_environment_credential():
    client_id = "fake-client-id"
    secret = "fake-client-secret"
    tenant_id = "fake-tenant-id"
    access_token = "***"

    transport = async_validating_transport(
        requests=[Request(url_substring=tenant_id, required_data={"client_id": client_id, "client_secret": secret})],
        responses=[
            mock_response(
                json_payload={
                    "token_type": "Bearer",
                    "expires_in": 42,
                    "ext_expires_in": 42,
                    "access_token": access_token,
                }
            )
        ],
    )

    environment = {
        EnvironmentVariables.AZURE_CLIENT_ID: client_id,
        EnvironmentVariables.AZURE_CLIENT_SECRET: secret,
        EnvironmentVariables.AZURE_TENANT_ID: tenant_id,
    }
    with mock.patch.dict("os.environ", environment, clear=True):
        token = await EnvironmentCredential(transport=transport).get_token("scope")

    assert token.token == access_token
