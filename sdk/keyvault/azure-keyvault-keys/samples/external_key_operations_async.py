# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys import ExternalKey
from azure.keyvault.keys.aio import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault Managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your Managed HSM
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, get, and delete permissions for your service principal in your Managed HSM
#
# 6. The Managed HSM is configured with an external HSM source that owns the key material referenced by external_key.id
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates External Key Management (EKM) operations against a Managed HSM that is backed by an
# external HSM. The external HSM owns the key material; Managed HSM stores a reference (`ExternalKey.id`) to
# that key.
#
# Note: External Key Management requires API version 2026-01-01-preview or later and is only supported on
# Managed HSM (not regular Key Vault).
#
# 1. Register a key whose material is owned by an external HSM (create_external_key)
#
# 2. Retrieve the key and inspect the external_key reference (get_key)
#
# 3. Delete the key registration (begin_delete_key)
#
# 4. Purge the key registration (purge_deleted_key)
# ----------------------------------------------------------------------------------------------------------


async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=MANAGED_HSM_URL, credential=credential)

    # Build an ExternalKey that references the key material managed in the external HSM.
    # The id must be at most 64 characters and may only contain letters, digits, and hyphens.
    print("\n.. Create an External Key")
    key_name = "externalKeyNameAsync"
    external_key = ExternalKey(id="external-key-reference-id")
    key = await client.create_external_key(key_name, external_key=external_key)
    assert key.properties.external_key is not None
    print(f"External key '{key.name}' was registered with external id '{key.properties.external_key.id}'.")
    print(f"Key type is '{key.key_type}' and key size is '{key.properties.key_size}'.")

    # Read the registration back to confirm the external_key reference is round-tripped.
    print("\n.. Get the External Key by name")
    fetched = await client.get_key(key.name)
    assert fetched.properties.external_key is not None
    print(f"Key with name '{fetched.name}' has external_key id '{fetched.properties.external_key.id}'.")
    print(f"Key type is '{fetched.key_type}' and key size is '{fetched.properties.key_size}'.")

    # The external key registration is no longer used; delete it from the Managed HSM.
    # Deleting the registration does not delete the key material in the external HSM.
    print("\n.. Delete the External Key")
    await client.delete_key(key.name)
    print(f"Deleted external key '{key.name}'.")

    # The deleted key registration still exists in the Managed HSM's soft-deleted state. Purge it to remove it permanently.
    print("\n.. Purge the deleted External Key")
    await client.purge_deleted_key(key.name)
    print(f"Purged external key '{key.name}'.")

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
