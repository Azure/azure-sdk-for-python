# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# 5. Key create, delete, recover, and purge permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates deleting and purging keys
#
# 1. Create a key (create_key)
#
# 2. Delete a key (delete_key)
#
# 3. Recover a deleted key (recover_deleted_key)
#
# 4. Purge a deleted key (purge_deleted_key)
# ----------------------------------------------------------------------------------------------------------
async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)

    print("\n.. Create keys")
    rsa_key = await client.create_rsa_key("rsaKeyNameAsync")
    ec_key = await client.create_ec_key("ecKeyNameAsync")
    print("Created key '{0}' of type '{1}'.".format(rsa_key.name, rsa_key.key_type))
    print("Created key '{0}' of type '{1}'.".format(ec_key.name, ec_key.key_type))

    print("\n.. Delete the keys")
    for key_name in (ec_key.name, rsa_key.name):
        deleted_key = await client.delete_key(key_name)
        print("Deleted key '{0}'".format(deleted_key.name))

    # A deleted key can only be recovered if the Key Vault is soft-delete enabled.
    print("\n.. Recover a deleted key")
    recovered_key = await client.recover_deleted_key(rsa_key.name)
    print("Recovered key '{0}'".format(recovered_key.name))

    # To permanently delete the key, the deleted key needs to be purged.
    await client.delete_key(recovered_key.name)

    # Keys will still purge eventually on their scheduled purge date, but calling `purge_deleted_key` immediately
    # purges.
    print("\n.. Purge keys")
    for key_name in (ec_key.name, rsa_key.name):
        await client.purge_deleted_key(key_name)
        print("Purged '{}'".format(key_name))

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
