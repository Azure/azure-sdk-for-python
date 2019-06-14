# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------


def test_create_vault_client():
    vault_url = "vault_url"
    # pylint:disable=unused-variable
    # [START create_vault_client]

    from azure.identity import DefaultAzureCredential
    from azure.security.keyvault import VaultClient

    # Create a VaultClient using default Azure credentials
    credential = DefaultAzureCredential()
    vault_client = VaultClient(vault_url, credential)

    # [END create_vault_client]
    try:
        # [START create_async_vault_client]

        from azure.identity.aio import AsyncDefaultAzureCredential
        from azure.security.keyvault.aio import VaultClient

        # Create a VaultClient using default Azure credentials
        credential = AsyncDefaultAzureCredential()
        vault_client = VaultClient(vault_url, credential)

        # [END create_async_vault_client]
    except (ImportError, SyntaxError):
        pass
