# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os

from azure.keyvault.administration.aio import KeyVaultBackupClient
from azure.identity.aio import ManagedIdentityCredential

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

async def run_sample():
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
    CONTAINER_URL = os.environ["CONTAINER_URL"]
    MANAGED_IDENTITY_CLIENT_ID = os.environ["CLIENT_ID"]

    # Instantiate a backup client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    credential = ManagedIdentityCredential(client_id=MANAGED_IDENTITY_CLIENT_ID)
    client = KeyVaultBackupClient(vault_url=MANAGED_HSM_URL, credential=credential)
    
    # Let's back up the vault with begin_backup, which returns a poller. Calling result() on the poller will return
    # a KeyVaultBackupResult that contains the URL of the backup after the operation completes. Calling wait() on
    # the poller will wait until the operation is complete.
    print("\n.. Back up the vault")
    backup_poller = await client.begin_backup(CONTAINER_URL, use_managed_identity=True)
    backup_result = await backup_poller.result()
    print("Vault backed up successfully.")
    assert backup_result.folder_url

    # Now let's the vault by calling begin_restore, which also returns a poller. Calling result() on the poller will
    # return None after the operation completes. Calling wait() on the poller will wait until the operation is
    # complete. To restore a single key from the backed up vault instead, pass the key_name keyword argument.
    print("\n.. Restore the full vault")
    restore_poller = await client.begin_restore(backup_result.folder_url, use_managed_identity=True)
    await restore_poller.wait()
    print("Vault restored successfully.")

    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
