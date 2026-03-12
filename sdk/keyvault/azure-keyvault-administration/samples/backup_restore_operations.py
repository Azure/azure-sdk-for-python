# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.administration import KeyVaultBackupResult

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM
#
# 4. A user-assigned managed identity that has access to your managed HSM. For more information about how to create a
#    user-assigned managed identity, refer to
#    https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview
#    
# 5. A storage account, that your managed identity has access to, containing a blob storage container
#    (See https://learn.microsoft.com/azure/storage/blobs/storage-blobs-introduction)
#
# 6. Set environment variables CONTAINER_URL and CLIENT_ID, corresponding to your blob container's URI and your
#    user-assigned managed identity's client ID, respectively.
#
# For more details, see https://learn.microsoft.com/azure/key-vault/managed-hsm/backup-restore
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates full backup and restore operations for Managed HSM
#
# 1. Perform a full backup (begin_backup)
#
# 2. Perform a full restore (begin_restore)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a backup client that will be used to call the service.
# Here we use the ManagedIdentityCredential to use Managed Identity, but any azure-identity credential can be used if
# opting for SAS token authentication.
# [START create_a_backup_restore_client]
from azure.identity import ManagedIdentityCredential
from azure.keyvault.administration import KeyVaultBackupClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
MANAGED_IDENTITY_CLIENT_ID = os.environ["CLIENT_ID"]
credential = ManagedIdentityCredential(client_id=MANAGED_IDENTITY_CLIENT_ID)
client = KeyVaultBackupClient(vault_url=MANAGED_HSM_URL, credential=credential)
# [END create_a_backup_restore_client]

# Let's back up the vault with begin_backup, which returns a poller. Calling result() on the poller will return a
# KeyVaultBackupResult that contains the URL of the backup after the operation completes. Calling wait() on the
# poller will wait until the operation is complete.
print("\n.. Back up the vault")
# [START begin_backup]
CONTAINER_URL = os.environ["CONTAINER_URL"]

backup_result: KeyVaultBackupResult = client.begin_backup(CONTAINER_URL, use_managed_identity=True).result()
print(f"Azure Storage Blob URL of the backup: {backup_result.folder_url}")
# [END begin_backup]
print("Vault backed up successfully.")
assert backup_result.folder_url

# Now let's the vault by calling begin_restore, which also returns a poller. Calling result() on the poller will
# return None after the operation completes. Calling wait() on the poller will wait until the operation is complete.
# To restore a single key from the backed up vault instead, pass the key_name keyword argument.
print("\n.. Restore the full vault")
# [START begin_restore]
# `backup_result` is the KeyVaultBackupResult returned by `begin_backup`
client.begin_restore(backup_result.folder_url, use_managed_identity=True).wait()
print("Vault restored successfully.")
# [END begin_restore]
