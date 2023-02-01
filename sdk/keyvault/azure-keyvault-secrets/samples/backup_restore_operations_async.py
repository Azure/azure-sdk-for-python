# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.keyvault.secrets.aio import SecretClient
from azure.identity.aio import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-secrets/
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
# 3. Delete a secret (delete_secret)
#
# 4. Purge a secret (purge_deleted_secret)
#
# 5. Restore a secret (restore_secret_backup)
# ----------------------------------------------------------------------------------------------------------
async def run_sample():
    # Instantiate a secret client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)

    # Let's create a secret holding storage account credentials.
    # if the secret already exists in the Key Vault, then a new version of the secret is created.
    print("\n.. Create Secret")
    secret = await client.set_secret("backupRestoreSecretNameAsync", "backupRestoreSecretValue")
    print(f"Secret with name '{secret.name}' created with value '{secret.value}'")

    # Backups are good to have, if in case secrets gets deleted accidentally.
    # For long term storage, it is ideal to write the backup to a file.
    print("\n.. Create a backup for an existing Secret")
    secret_backup = await client.backup_secret(secret.name)
    print(f"Backup created for secret with name '{secret.name}'.")

    # The storage account secret is no longer in use, so you delete it.
    print("\n.. Deleting secret...")
    await client.delete_secret(secret.name)
    print(f"Deleted secret with name '{secret.name}'")

    # Purge the deleted secret.
    # The purge will take some time, so wait before restoring the backup to avoid a conflict.
    print("\n.. Purge the secret")
    await client.purge_deleted_secret(secret.name)
    await asyncio.sleep(60)
    print(f"Purged secret with name '{secret.name}'")

    # In the future, if the secret is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the secret using the backed up secret bytes")
    secret = await client.restore_secret_backup(secret_backup)
    print(f"Restored secret with name '{secret.name}'")

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())