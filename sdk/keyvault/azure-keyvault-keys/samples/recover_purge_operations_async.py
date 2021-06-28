# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.keyvault.keys.aio import KeyClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-keys/
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates deleting and purging a vault(key) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
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
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)
    try:
        print("\n.. Create keys")
        rsa_key = await client.create_rsa_key("rsaKeyName")
        ec_key = await client.create_ec_key("ecKeyName")
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

        # deleting the recovered key so it doesn't outlast this script
        # If the keyvault is soft-delete enabled, then for permanent deletion, the deleted key needs to be purged.
        await client.delete_key(recovered_key.name)

        # Keys will still purge eventually on their scheduled purge date, but calling `purge_deleted_key` immediately
        # purges.
        print("\n.. Purge keys")
        for key_name in (ec_key.name, rsa_key.name):
            await client.purge_deleted_key(key_name)
            print("Purged '{}'".format(key_name))

    except HttpResponseError as e:
        if "(NotSupported)" in e.message:
            print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
        else:
            print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")
        await credential.close()
        await client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
