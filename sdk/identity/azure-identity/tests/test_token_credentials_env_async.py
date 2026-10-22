# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from unittest.mock import patch

import pytest

from azure.identity.aio import (
    AzureCliCredential,
    AzureDeveloperCliCredential,
    AzurePowerShellCredential,
    DefaultAzureCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    WorkloadIdentityCredential,
)
from azure.identity._constants import EnvironmentVariables

from helpers import mock_response, Request, GET_TOKEN_METHODS
from helpers_async import async_validating_transport


def test_token_credentials_env_dev():
    """With AZURE_TOKEN_CREDENTIALS=dev, DefaultAzureCredential should use only developer credentials"""

    prod_credentials = {EnvironmentCredential, WorkloadIdentityCredential, ManagedIdentityCredential}

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "dev"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # All dev credentials should be present (if supported)
        if SharedTokenCacheCredential.supported():
            assert SharedTokenCacheCredential in actual_classes

        # Other developer credentials should be present
        assert AzureCliCredential in actual_classes
        assert AzureDeveloperCliCredential in actual_classes
        assert AzurePowerShellCredential in actual_classes

        # Assert no duplicates
        assert len(actual_classes) == len(set(actual_classes))

        # Production credentials should NOT be present
        for cred_class in prod_credentials:
            if cred_class == WorkloadIdentityCredential:
                # Skip this check unless env vars are set
                if not all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS):
                    continue
            assert cred_class not in actual_classes


def test_token_credentials_env_prod():
    """With AZURE_TOKEN_CREDENTIALS=prod, DefaultAzureCredential should use only production credentials"""

    dev_credentials = {
        SharedTokenCacheCredential,
        AzureCliCredential,
        AzureDeveloperCliCredential,
        AzurePowerShellCredential,
    }

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "prod"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Production credentials should be present
        assert EnvironmentCredential in actual_classes
        assert ManagedIdentityCredential in actual_classes

        # Check WorkloadIdentityCredential only if env vars are set
        if all(os.environ.get(var) for var in EnvironmentVariables.WORKLOAD_IDENTITY_VARS):
            assert WorkloadIdentityCredential in actual_classes

        # Assert no duplicates
        assert len(actual_classes) == len(set(actual_classes))

        # Developer credentials should NOT be present
        for cred_class in dev_credentials:
            assert cred_class not in actual_classes


def test_token_credentials_env_case_insensitive():
    """AZURE_TOKEN_CREDENTIALS should be case insensitive"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "DeV"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # EnvironmentCredential (prod) should not be present
        assert EnvironmentCredential not in actual_classes

        # AzureCliCredential (dev) should be present
        assert AzureCliCredential in actual_classes


def test_token_credentials_env_invalid():
    """Invalid AZURE_TOKEN_CREDENTIALS value should raise an error"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "invalid"}, clear=False):
        with pytest.raises(ValueError):
            credential = DefaultAzureCredential()


def test_token_credentials_env_with_exclude():
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "prod"}, clear=False):
        credential = DefaultAzureCredential(exclude_environment_credential=True)
        actual_classes = [c.__class__ for c in credential.credentials]

        assert EnvironmentCredential not in actual_classes


def test_token_credentials_env_workload_identity_credential():
    """With AZURE_TOKEN_CREDENTIALS=WorkloadIdentityCredential, only WorkloadIdentityCredential should be used"""

    with patch.dict(
        "os.environ",
        {
            EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "WorkloadIdentityCredential",
            EnvironmentVariables.AZURE_AUTHORITY_HOST: "https://login.microsoftonline.com",
            EnvironmentVariables.AZURE_TENANT_ID: "tenant-id",
            EnvironmentVariables.AZURE_CLIENT_ID: "client-id",
            EnvironmentVariables.AZURE_FEDERATED_TOKEN_FILE: "/tmp/token",
        },
        clear=False,
    ):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Only WorkloadIdentityCredential should be present
        assert WorkloadIdentityCredential in actual_classes
        assert len(actual_classes) == 1


def test_token_credentials_env_environment_credential():
    """With AZURE_TOKEN_CREDENTIALS=EnvironmentCredential, only EnvironmentCredential should be used"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "EnvironmentCredential"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Only EnvironmentCredential should be present
        assert EnvironmentCredential in actual_classes
        assert len(actual_classes) == 1


def test_token_credentials_env_managed_identity_credential():
    """With AZURE_TOKEN_CREDENTIALS=ManagedIdentityCredential, only ManagedIdentityCredential should be used"""

    with patch.dict(
        "os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "ManagedIdentityCredential"}, clear=False
    ):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Only ManagedIdentityCredential should be present
        assert ManagedIdentityCredential in actual_classes
        assert len(actual_classes) == 1


def test_token_credentials_env_azure_cli_credential():
    """With AZURE_TOKEN_CREDENTIALS=AzureCliCredential, only AzureCliCredential should be used"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "AzureCliCredential"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Only AzureCliCredential should be present
        assert AzureCliCredential in actual_classes
        assert len(actual_classes) == 1


def test_token_credentials_env_specific_credential_case_insensitive():
    """Specific credential names should be case insensitive"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "environmentcredential"}, clear=False):
        credential = DefaultAzureCredential()

        # Get the actual credential classes in the chain
        actual_classes = [c.__class__ for c in credential.credentials]

        # Only EnvironmentCredential should be present
        assert EnvironmentCredential in actual_classes
        assert len(actual_classes) == 1


def test_token_credentials_env_invalid_specific_credential():
    """Invalid specific credential name should raise an error"""

    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "InvalidCredential"}, clear=False):
        with pytest.raises(ValueError) as exc_info:
            credential = DefaultAzureCredential()

        error_msg = str(exc_info.value)
        assert "Invalid value" in error_msg

    # Test case: specific credential that is not supported
    # For example, SharedTokenCacheCredential is not supported in this context
    with patch.dict(
        "os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "sharedtokencachecredential"}, clear=True
    ):
        with pytest.raises(ValueError):
            DefaultAzureCredential()

        error_msg = str(exc_info.value)
        assert "Invalid value" in error_msg


def test_user_exclude_flags_override_env_var():
    """User-provided exclude flags should take precedence over AZURE_TOKEN_CREDENTIALS environment variable"""

    # Test case 1: env var says use specific credential, but user excludes it (should result in empty chain)
    with patch.dict(
        "os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "azurepowershellcredential"}, clear=False
    ):
        with pytest.raises(ValueError, match="at least one credential is required"):
            DefaultAzureCredential(exclude_powershell_credential=True)

    # Test case 2: env var says use specific credential, user includes additional credential
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "environmentcredential"}, clear=False):
        credential = DefaultAzureCredential(exclude_powershell_credential=False)
        actual_classes = [c.__class__ for c in credential.credentials]

        # Both EnvironmentCredential and AzurePowerShellCredential should be present
        assert EnvironmentCredential in actual_classes
        assert AzurePowerShellCredential in actual_classes

    # Test case 3: env var says "dev" mode, user excludes a dev credential
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "dev"}, clear=False):
        credential = DefaultAzureCredential(exclude_cli_credential=True)
        actual_classes = [c.__class__ for c in credential.credentials]

        # AzureCliCredential should NOT be present despite "dev" mode
        assert AzureCliCredential not in actual_classes
        # Other dev credentials should still be present
        assert AzurePowerShellCredential in actual_classes
        assert AzureDeveloperCliCredential in actual_classes


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_imds_credential_skips_probe_when_token_credentials_env_set_async(get_token_method):
    """Test that async ImdsCredential skips the endpoint probe when AZURE_TOKEN_CREDENTIALS is set to "managedidentitycredential" """

    # Create a transport that would fail the probe but succeed for the actual token request
    token_response = mock_response(
        json_payload={
            "access_token": "token",
            "expires_in": 42,
            "expires_on": int(time.time()) + 42,
            "ext_expires_in": 42,
            "not_before": int(time.time()),
            "resource": "scope",
            "token_type": "Bearer",
        }
    )

    # Use a transport that would normally fail the probe (connection_timeout=1, retry_total=0)
    # but should succeed for the actual token request
    transport = async_validating_transport(
        requests=[Request()], responses=[token_response]  # Only expect one request (no probe)
    )

    with patch.dict(os.environ, {EnvironmentVariables.AZURE_TOKEN_CREDENTIALS: "managedidentitycredential"}):

        credential = DefaultAzureCredential(transport=transport)

        # This should succeed without calling the probe
        token = await getattr(credential, get_token_method)("scope")
        assert token.token == "token"
