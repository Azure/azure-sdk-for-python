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
# 5. Key create, backup, delete, purge, and restore permissions for your service principal in your vault
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
# 4. Purge a key (purge_deleted_key)
#
# 5. Restore a key (restore_key_backup)
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)
    
    # Let's create a Key of type RSA.
    # if the key already exists in the Key Vault, then a new version of the key is created.
    print("\n.. Create Key")
    key = await client.create_key("keyNameAsync", "RSA")
    print("Key with name '{0}' created with key type '{1}'".format(key.name, key.key_type))

    # Backups are good to have, if in case keys gets deleted accidentally.
    # For long term storage, it is ideal to write the backup to a file.
    print("\n.. Create a backup for an existing Key")
    key_backup = await client.backup_key(key.name)
    print("Backup created for key with name '{0}'.".format(key.name))

    # The rsa key is no longer in use, so you delete it.
    deleted_key = await client.delete_key(key.name)
    print("Deleted key with name '{0}'".format(deleted_key.name))

    # Purge the deleted key.
    # The purge will take some time, so wait before restoring the backup to avoid a conflict.
    print("\n.. Purge the key")
    await client.purge_deleted_key(key.name)
    await asyncio.sleep(60)
    print("Purged key with name '{0}'".format(deleted_key.name))

    # In the future, if the key is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the key using the backed up key bytes")
    key = await client.restore_key_backup(key_backup)
    print("Restored key with name '{0}'".format(key.name))

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
