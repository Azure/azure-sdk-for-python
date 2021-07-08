# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.administration import KeyVaultBackupClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration#authenticate-the-client)
#
# 4. A storage account containing a blob storage container
#    (See https://docs.microsoft.com/azure/storage/blobs/storage-blobs-introduction)
#
# 5. Set Environment variables CONTAINER_URL and SAS_TOKEN corresponding to your blob container's URI and SAS
#    (See https://docs.microsoft.com/azure/storage/common/storage-sas-overview)
#
# For more details, see https://docs.microsoft.com/azure/key-vault/managed-hsm/backup-restore
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates vault backup and restore operations for Managed HSM
#
# 1. Back up a full vault (begin_backup)
#
# 2. Restore a full vault (begin_restore)
# ----------------------------------------------------------------------------------------------------------

VAULT_URL = os.environ["VAULT_URL"]
CONTAINER_URL = os.environ["CONTAINER_URL"]
SAS_TOKEN = os.environ["SAS_TOKEN"]

# Instantiate a backup client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
credential = DefaultAzureCredential()
client = KeyVaultBackupClient(vault_url=VAULT_URL, credential=credential)
try:
    # Let's back up the vault with begin_backup, which returns a poller. Calling result() on the poller will return a
    # KeyVaultBackupResult that contains the URL of the backup after the operation completes. Calling wait() on the
    # poller will wait until the operation is complete.
    print("\n.. Back up the vault")
    backup_result = client.begin_backup(CONTAINER_URL, SAS_TOKEN).result()
    print("Vault backed up successfully.")

    # Now let's the vault by calling begin_restore, which also returns a poller. Calling result() on the poller will
    # return None after the operation completes. Calling wait() on the poller will wait until the operation is complete.
    # To restore a single key from the backed up vault instead, pass the key_name keyword argument.
    print("\n.. Restore the full vault")
    client.begin_restore(backup_result.folder_url, SAS_TOKEN).wait()
    print("Vault restored successfully.")

except HttpResponseError as e:
    print("\nThis sample has caught an error. {}".format(e.message))
