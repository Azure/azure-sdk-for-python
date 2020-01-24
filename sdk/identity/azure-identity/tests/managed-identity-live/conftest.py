# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

import pytest

if sys.version_info < (3, 5, 3):
    collect_ignore_glob = ["*_async.py"]

AZURE_IDENTITY_TEST_VAULT_URL = "AZURE_IDENTITY_TEST_VAULT_URL"
AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID = "AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID"


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
