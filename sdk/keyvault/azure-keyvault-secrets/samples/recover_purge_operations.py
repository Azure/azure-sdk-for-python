# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-secrets and azure-identity libraries (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates deleting and purging a vault(secret) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
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
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Let's create secrets holding storage and bank accounts credentials. If the secret
# already exists in the Key Vault, then a new version of the secret is created.
print("\n.. Create Secret")
bank_secret = client.set_secret("recoverPurgeBankSecretName", "recoverPurgeSecretValue1")
storage_secret = client.set_secret("recoverPurgeStorageSecretName", "recoverPurgeSecretValue2")
print("Secret with name '{0}' was created.".format(bank_secret.name))
print("Secret with name '{0}' was created.".format(storage_secret.name))

# The storage account was closed, so we need to delete its credentials from the Key Vault.
print("\n.. Delete a Secret")
delete_secret_poller = client.begin_delete_secret(bank_secret.name)
secret = delete_secret_poller.result()
delete_secret_poller.wait()
print("Secret with name '{0}' was deleted on date {1}.".format(secret.name, secret.deleted_date))

# We accidentally deleted the bank account secret. Let's recover it.
# A deleted secret can only be recovered if the Key Vault is soft-delete enabled.
print("\n.. Recover Deleted Secret")
recover_secret_poller = client.begin_recover_deleted_secret(bank_secret.name)
recovered_secret = recover_secret_poller.result()

# This wait is just to ensure recovery is complete before we delete the secret again
recover_secret_poller.wait()
print("Recovered Secret with name '{0}'.".format(recovered_secret.name))

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
