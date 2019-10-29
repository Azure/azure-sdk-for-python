# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-secrets and azure-identity libraries (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
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
# 4. Restore a secret (restore_secret_backup)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a secret client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)
try:
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
    deleted_secret = client.begin_delete_secret(secret.name).result()
    print("Deleted Secret with name '{0}'".format(deleted_secret.name))

    # In future, if the secret is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the secret using the backed up secret bytes")
    secret = client.restore_secret_backup(secret_backup)
    print("Restored Secret with name '{0}'".format(secret.name))

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
