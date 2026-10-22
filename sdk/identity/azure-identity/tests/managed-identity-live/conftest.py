# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

from azure.identity._constants import EnvironmentVariables
import pytest

AZURE_IDENTITY_TEST_VAULT_URL = "AZURE_IDENTITY_TEST_VAULT_URL"
AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID = "AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID"


def pytest_configure(config):
    config.addinivalue_line("markers", "cloudshell: test requires a Cloud Shell environment")


@pytest.fixture()
def live_managed_identity_config():
    """Live managed identity tests interact with a service to verify the credential acquires a valid access token.

    These tests use the Key Vault Secrets API. They therefore require azure-keyvault-secrets and the URL of a Key Vault
    in $AZURE_IDENTITY_TEST_VAULT_URL. They also use the value of $AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID to
    (optionally) test user-assigned managed identity; that value should be the client ID of an Azure Managed Identity.
    """

    try:
        import azure.keyvault.secrets

        return {
            "vault_url": os.environ[AZURE_IDENTITY_TEST_VAULT_URL],
            "client_id": os.environ.get(AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID),
        }
    except ImportError:
        pytest.skip("this test requires azure-keyvault-secrets")
    except KeyError:
        pytest.skip("this test requires a Key Vault URL in $" + AZURE_IDENTITY_TEST_VAULT_URL)


@pytest.fixture()
def cloud_shell():
    """Cloud Shell MSI is distinguished by a value for MSI_ENDPOINT but not MSI_SECRET."""

    if EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET in os.environ:
        pytest.skip("Cloud Shell MSI unavailable")
        return

    try:
        return {"vault_url": os.environ[AZURE_IDENTITY_TEST_VAULT_URL]}
    except KeyError:
        pytest.skip("this test requires a Key Vault URL in $" + AZURE_IDENTITY_TEST_VAULT_URL)
