import asyncio
import os
from azure.keyvault.keys.aio import KeyClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-keys/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic backup and restore operations on a vault(key) resource for Azure Key Vault
#
# 1. Create a key (create_key)
#
# 2. Backup a key (backup_key)
#
# 3. Delete a key (delete_key)
#
# 4. Restore a key (restore_key)
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
        # Let's create a Key of type RSA.
        # if the key already exists in the Key Vault, then a new version of the key is created.
        print("\n1. Create Key")
        key = await client.create_key("keyName", "RSA")
        print("Key with name '{0}' created with key type '{1}'".format(key.name, key.key_material.kty))

        # Backups are good to have, if in case keys gets deleted accidentally.
        # For long term storage, it is ideal to write the backup to a file.
        print("\n1. Create a backup for an existing Key")
        key_backup = await client.backup_key(key.name)
        print("Backup created for key with name '{0}'.".format(key.name))

        # The rsa key is no longer in use, so you delete it.
        await client.delete_key(key.name)

        # To ensure key is deleted on the server side.
        print("\nDeleting key...")
        print("Deleted Key with name '{0}'".format(key.name))

        # In future, if the key is required again, we can use the backup value to restore it in the Key Vault.
        print("\n2. Restore the key using the backed up key bytes")
        key = await client.restore_key(key_backup)
        print("Restored Key with name '{0}'".format(key.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
