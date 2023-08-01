# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. A storage account containing a blob storage container
#    (See https://docs.microsoft.com/azure/storage/blobs/storage-blobs-introduction)
#
# 6. Set environment variables CONTAINER_URL and SAS_TOKEN corresponding to your blob container's URI and SAS
#    (See https://docs.microsoft.com/azure/storage/common/storage-sas-overview)
#
# For more details, see https://docs.microsoft.com/azure/key-vault/managed-hsm/backup-restore
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates full backup and restore operations for Managed HSM
#
# 1. Perform a full backup (begin_backup)
#
# 2. Perform a full restore (begin_restore)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a backup client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_a_backup_restore_client]
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultBackupClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultBackupClient(vault_url=MANAGED_HSM_URL, credential=credential)
# [END create_a_backup_restore_client]

# Let's back up the vault with begin_backup, which returns a poller. Calling result() on the poller will return a
# KeyVaultBackupResult that contains the URL of the backup after the operation completes. Calling wait() on the
# poller will wait until the operation is complete.
print("\n.. Back up the vault")
# [START begin_backup]
CONTAINER_URL = os.environ["CONTAINER_URL"]
SAS_TOKEN = os.environ["SAS_TOKEN"]

backup_result = client.begin_backup(CONTAINER_URL, SAS_TOKEN).result()
print(f"Azure Storage Blob URL of the backup: {backup_result.folder_url}")
# [END begin_backup]
print("Vault backed up successfully.")

# Now let's the vault by calling begin_restore, which also returns a poller. Calling result() on the poller will
# return None after the operation completes. Calling wait() on the poller will wait until the operation is complete.
# To restore a single key from the backed up vault instead, pass the key_name keyword argument.
print("\n.. Restore the full vault")
# [START begin_restore]
client.begin_restore(backup_result.folder_url, SAS_TOKEN).wait()
# [END begin_restore]
print("Vault restored successfully.")
