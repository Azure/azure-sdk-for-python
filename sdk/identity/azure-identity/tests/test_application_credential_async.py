# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken
from azure.identity import CredentialUnavailableError
from azure.identity.aio._credentials.application import AzureApplicationCredential
from azure.identity._constants import EnvironmentVariables
import pytest
from urllib.parse import urlparse

from helpers import build_aad_response, mock_response
from helpers_async import get_completed_future


@pytest.mark.asyncio
async def test_iterates_only_once():
    """When a credential succeeds, AzureApplicationCredential should use that credential thereafter"""

    expected_token = AccessToken("***", 42)
    unavailable_credential = Mock(get_token=Mock(side_effect=CredentialUnavailableError(message="...")))
    successful_credential = Mock(get_token=Mock(return_value=get_completed_future(expected_token)))

    credential = AzureApplicationCredential()
    credential.credentials = [
        unavailable_credential,
        successful_credential,
        Mock(get_token=Mock(side_effect=Exception("iteration didn't stop after a credential provided a token"))),
    ]

    for n in range(3):
        token = await credential.get_token("scope")
        assert token.token == expected_token.token
        assert unavailable_credential.get_token.call_count == 1
        assert successful_credential.get_token.call_count == n + 1


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept authority configuration by keyword argument or environment"""

    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority  # "localhost" parses to netloc "", path "localhost"

    def test_initialization(mock_credential, expect_argument):
        AzureApplicationCredential(authority=authority)
        assert mock_credential.call_count == 1

        # N.B. if os.environ has been patched somewhere in the stack, that patch is in place here
        environment = dict(os.environ, **{EnvironmentVariables.AZURE_AUTHORITY_HOST: authority})
        with patch.dict(AzureApplicationCredential.__module__ + ".os.environ", environment, clear=True):
            AzureApplicationCredential()
        assert mock_credential.call_count == 2

        for _, kwargs in mock_credential.call_args_list:
            if expect_argument:
                actual = urlparse(kwargs["authority"])
                assert actual.scheme == "https"
                assert actual.netloc == expected_netloc
            else:
                assert "authority" not in kwargs

    # authority should be passed to EnvironmentCredential as a keyword argument
    environment = {var: "foo" for var in EnvironmentVariables.CLIENT_SECRET_VARS}
    with patch(AzureApplicationCredential.__module__ + ".EnvironmentCredential") as mock_credential:
        with patch.dict("os.environ", environment, clear=True):
            test_initialization(mock_credential, expect_argument=True)

    # authority should not be passed to ManagedIdentityCredential
    with patch(AzureApplicationCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
        with patch.dict("os.environ", {EnvironmentVariables.MSI_ENDPOINT: "localhost"}, clear=True):
            test_initialization(mock_credential, expect_argument=False)


@pytest.mark.asyncio
async def test_get_token():
    expected_token = "***"

    async def send(request, **kwargs):
        # ensure the `claims` and `tenant_id` keywords from credential's `get_token` method don't make it to transport
        assert "claims" not in kwargs
        assert "tenant_id" not in kwargs
        return mock_response(json_payload=build_aad_response(access_token=expected_token))

    with patch.dict("os.environ", {var: "..." for var in EnvironmentVariables.CLIENT_SECRET_VARS}, clear=True):
        credential = AzureApplicationCredential(transport=Mock(send=send))

    token = await credential.get_token("scope")
    assert token.token == expected_token


def test_managed_identity_client_id():
    """the credential should accept a user-assigned managed identity's client ID by kwarg or environment variable"""

    expected_args = {"client_id": "the-client"}

    with patch(AzureApplicationCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
        AzureApplicationCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)

    # client id can also be specified in $AZURE_CLIENT_ID
    with patch.dict(os.environ, {EnvironmentVariables.AZURE_CLIENT_ID: expected_args["client_id"]}, clear=True):
        with patch(AzureApplicationCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
            AzureApplicationCredential()
    mock_credential.assert_called_once_with(**expected_args)

    # keyword argument should override environment variable
    with patch.dict(
        os.environ, {EnvironmentVariables.AZURE_CLIENT_ID: "not-" + expected_args["client_id"]}, clear=True
    ):
        with patch(AzureApplicationCredential.__module__ + ".ManagedIdentityCredential") as mock_credential:
            AzureApplicationCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)
