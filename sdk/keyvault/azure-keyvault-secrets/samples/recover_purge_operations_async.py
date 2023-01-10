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
# 2. azure-keyvault-secrets and azure-identity libraries (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates deleting and purging a vault(secret) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
#
# 1. Create a secret (set_secret)
#
# 2. Delete a secret (delete_secret)
#
# 3. Recover a deleted secret (recover_deleted_secret)
#
# 4. Purge a deleted secret (purge_deleted_secret)
# ----------------------------------------------------------------------------------------------------------
async def run_sample():
    # Instantiate a secret client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)

    # Let's create secrets holding storage and bank accounts credentials. If the secret
    # already exists in the Key Vault, then a new version of the secret is created.
    print("\n.. Create Secret")
    bank_secret = await client.set_secret("recoverPurgeBankSecretNameAsync", "recoverPurgeSecretValue1")
    storage_secret = await client.set_secret("recoverPurgeStorageSecretNameAsync", "recoverPurgeSecretValue2")
    print(f"Secret with name '{bank_secret.name}' was created.")
    print(f"Secret with name '{storage_secret.name}' was created.")

    # The storage account was closed, need to delete its credentials from the Key Vault.
    print("\n.. Delete a Secret")
    secret = await client.delete_secret(bank_secret.name)
    print(f"Secret with name '{secret.name}' was deleted on date {secret.deleted_date}.")

    # We accidentally deleted the bank account secret. Let's recover it.
    # A deleted secret can only be recovered if the Key Vault is soft-delete enabled.
    print("\n.. Recover Deleted Secret")
    recovered_secret = await client.recover_deleted_secret(bank_secret.name)
    print(f"Recovered Secret with name '{recovered_secret.name}'.")

    # Let's delete storage account now.
    # If the keyvault is soft-delete enabled, then for permanent deletion, the deleted secret needs to be purged.
    print("\n.. Deleting secret...")
    await client.delete_secret(storage_secret.name)

    # Secrets will still purge eventually on their scheduled purge date, but calling `purge_deleted_secret` immediately
    # purges.
    print("\n.. Purge Deleted Secret")
    await client.purge_deleted_secret(storage_secret.name)
    print("Secret has been permanently deleted.")

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
