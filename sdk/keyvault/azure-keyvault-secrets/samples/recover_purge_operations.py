# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
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
# Sample - demonstrates deleting and purging a vault(secret) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
#
# 1. Create a secret (set_secret)
#
# 2. Delete a secret (begin_delete_secret)
#
# 3. Recover a deleted secret (begin_recover_deleted_secret)
#
# 4. Purge a deleted secret (purge_deleted_secret)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a secret client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Let's create secrets holding storage and bank accounts credentials. If the secret
# already exists in the Key Vault, then a new version of the secret is created.
print("\n.. Create Secret")
bank_secret = client.set_secret("recoverPurgeBankSecretName", "recoverPurgeSecretValue1")
storage_secret = client.set_secret("recoverPurgeStorageSecretName", "recoverPurgeSecretValue2")
print(f"Secret with name '{bank_secret.name}' was created.")
print(f"Secret with name '{storage_secret.name}' was created.")

# The storage account was closed, so we need to delete its credentials from the Key Vault.
print("\n.. Delete a Secret")
delete_secret_poller = client.begin_delete_secret(bank_secret.name)
secret = delete_secret_poller.result()
delete_secret_poller.wait()
print(f"Secret with name '{secret.name}' was deleted on date {secret.deleted_date}.")

# We accidentally deleted the bank account secret. Let's recover it.
# A deleted secret can only be recovered if the Key Vault is soft-delete enabled.
print("\n.. Recover Deleted Secret")
recover_secret_poller = client.begin_recover_deleted_secret(bank_secret.name)
recovered_secret = recover_secret_poller.result()

# This wait is just to ensure recovery is complete before we delete the secret again
recover_secret_poller.wait()
print(f"Recovered Secret with name '{recovered_secret.name}'.")

# Let's delete the storage secret now.
# If the keyvault is soft-delete enabled, then for permanent deletion, the deleted secret needs to be purged.
# Calling result() on the method will immediately return the `DeletedSecret`, but calling wait() blocks
# until the secret is deleted server-side so it can be purged.
print("\n.. Deleting secret...")
client.begin_delete_secret(storage_secret.name).wait()

# Secrets will still purge eventually on their scheduled purge date, but calling `purge_deleted_secret` immediately
# purges.
print("\n.. Purge Deleted Secret")
client.purge_deleted_secret(storage_secret.name)
print("Secret has been permanently deleted.")
