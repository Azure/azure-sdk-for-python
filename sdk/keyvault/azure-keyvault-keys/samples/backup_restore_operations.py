# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
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
# 3. Delete a key (begin_delete_key)
#
# 4. Purge a key (purge_deleted_key)
#
# 5. Restore a key (restore_key_backup)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a key client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)

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
delete_operation = client.begin_delete_key(key.name)
deleted_key = delete_operation.result()
print("Deleted key with name '{0}'".format(deleted_key.name))

# Wait for the deletion to complete before purging the key.
# The purge will take some time, so wait before restoring the backup to avoid a conflict.
delete_operation.wait()
print("\n.. Purge the key")
client.purge_deleted_key(key.name)
time.sleep(60)
print("Purged key with name '{0}'".format(deleted_key.name))

# In the future, if the key is required again, we can use the backup value to restore it in the Key Vault.
print("\n.. Restore the key using the backed up key bytes")
key = client.restore_key_backup(key_backup)
print("Restored key with name '{0}'".format(key.name))
