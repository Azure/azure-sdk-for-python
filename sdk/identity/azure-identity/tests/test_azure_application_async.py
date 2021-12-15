# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import patch

from azure.identity.aio._credentials.application import AzureApplicationCredential
from azure.identity._constants import EnvironmentVariables


def test_managed_identity_client_id():
    """the credential should accept a user-assigned managed identity's client ID by kwarg or environment variable"""

    expected_args = {"client_id": "the client"}

    ENVIRON = AzureApplicationCredential.__module__ + ".os.environ"
    MANAGED_IDENTITY_CREDENTIAL = AzureApplicationCredential.__module__ + ".ManagedIdentityCredential"

    with patch(MANAGED_IDENTITY_CREDENTIAL) as mock_credential:
        AzureApplicationCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)

    # client id can also be specified in $AZURE_CLIENT_ID
    with patch.dict(ENVIRON, {EnvironmentVariables.AZURE_CLIENT_ID: expected_args["client_id"]}, clear=True):
        with patch(MANAGED_IDENTITY_CREDENTIAL) as mock_credential:
            AzureApplicationCredential()
    mock_credential.assert_called_once_with(**expected_args)

    # keyword argument should override environment variable
    with patch.dict(ENVIRON, {EnvironmentVariables.AZURE_CLIENT_ID: "not-" + expected_args["client_id"]}, clear=True):
        with patch(MANAGED_IDENTITY_CREDENTIAL) as mock_credential:
            AzureApplicationCredential(managed_identity_client_id=expected_args["client_id"])
    mock_credential.assert_called_once_with(**expected_args)
