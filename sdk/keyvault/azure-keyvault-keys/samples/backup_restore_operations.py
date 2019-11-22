# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.keyvault.keys import KeyClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic backup and restore operations on a vault(key) resource for Azure Key Vault
#
# 1. Create a key (create_key)
#
# 2. Backup a key (backup_key)
#
# 3. Delete a key (begin_delete_key)
#
# 4. Restore a key (restore_key_backup)
# ----------------------------------------------------------------------------------------------------------

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
    print("\n.. Create Key")
    key = client.create_key("keyName", "RSA")
    print("Key with name '{0}' created with key type '{1}'".format(key.name, key.key_type))

    # Backups are good to have, if in case keys gets deleted accidentally.
    # For long term storage, it is ideal to write the backup to a file.
    print("\n.. Create a backup for an existing Key")
    key_backup = client.backup_key(key.name)
    print("Backup created for key with name '{0}'.".format(key.name))

    # The rsa key is no longer in use, so you delete it.
    print("\n.. Delete the key")
    deleted_key = client.begin_delete_key(key.name).result()
    print("Deleted Key with name '{0}'".format(deleted_key.name))

    # In future, if the key is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the key using the backed up key bytes")
    key = client.restore_key_backup(key_backup)
    print("Restored Key with name '{0}'".format(key.name))

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
