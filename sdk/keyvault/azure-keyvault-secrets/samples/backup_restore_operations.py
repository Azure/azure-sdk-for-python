# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-secrets and azure-identity libraries (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic backup and restore operations on a vault(secret) resource for Azure Key Vault
#
# 1. Create a secret (set_secret)
#
# 2. Backup a secret (backup_secret)
#
# 3. Delete a secret (begin_delete_secret)
#
# 4. Purge a secret (purge_deleted_secret)
#
# 5. Restore a secret (restore_secret_backup)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a secret client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Let's create a secret holding storage account credentials.
# if the secret already exists in the Key Vault, then a new version of the secret is created.
print("\n.. Create Secret")
secret = client.set_secret("backupRestoreSecretName", "backupRestoreSecretValue")
print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))

# Backups are good to have, if in case secrets gets deleted accidentally.
# For long term storage, it is ideal to write the backup to a file.
print("\n.. Create a backup for an existing Secret")
secret_backup = client.backup_secret(secret.name)
print("Backup created for secret with name '{0}'.".format(secret.name))

# The storage account secret is no longer in use, so you delete it.
print("\n.. Deleting secret...")
delete_operation = client.begin_delete_secret(secret.name)
deleted_secret = delete_operation.result()
print("Deleted secret with name '{0}'".format(deleted_secret.name))

# Wait for the deletion to complete before purging the secret.
# The purge will take some time, so wait before restoring the backup to avoid a conflict.
delete_operation.wait()
print("\n.. Purge the secret")
client.purge_deleted_secret(deleted_secret.name)
time.sleep(60)
print("Purged secret with name '{0}'".format(deleted_secret.name))

# In the future, if the secret is required again, we can use the backup value to restore it in the Key Vault.
print("\n.. Restore the secret using the backed up secret bytes")
secret = client.restore_secret_backup(secret_backup)
print("Restored secret with name '{0}'".format(secret.name))
