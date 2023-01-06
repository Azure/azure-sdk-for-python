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
# Sample - demonstrates the basic list operations on a vault(secret) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
#
# 1. Create secret (set_secret)
#
# 2. List secrets from the Key Vault (list_secrets)
#
# 3. List secret versions from the Key Vault (list_properties_of_secret_versions)
#
# 4. List deleted secrets from the Key Vault (list_deleted_secrets). The vault has to be soft-delete enabled to perform
# this operation.
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a secret client that will be used to call the service. Notice that the client is using default Azure
# credentials. To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)

# Let's create secrets holding storage and bank accounts credentials. If the secret
# already exists in the Key Vault, then a new version of the secret is created.
print("\n.. Create Secret")
bank_secret = client.set_secret("listOpsBankSecretName", "listOpsSecretValue1")
storage_secret = client.set_secret("listOpsStorageSecretName", "listOpsSecretValue2")
print("Secret with name '{0}' was created.".format(bank_secret.name))
print("Secret with name '{0}' was created.".format(storage_secret.name))

# You need to check if any of the secrets are sharing same values.
# Let's list the secrets and print their values.
# List operations don 't return the secrets with value information.
# So, for each returned secret we call get_secret to get the secret with its value information.
print("\n.. List secrets from the Key Vault")
secrets = client.list_properties_of_secrets()
for secret in secrets:
    retrieved_secret = client.get_secret(secret.name)
    print(
        "Secret with name '{0}' and value {1} was found.".format(retrieved_secret.name, retrieved_secret.name)
    )

# The bank account password got updated, so you want to update the secret in Key Vault to ensure it reflects the
# new password. Calling set_secret on an existing secret creates a new version of the secret in the Key Vault
# with the new value.
updated_secret = client.set_secret(bank_secret.name, "newSecretValue")
print(
    "Secret with name '{0}' was updated with new value '{1}'".format(updated_secret.name, updated_secret.value)
)

# You need to check all the different values your bank account password secret had previously. Lets print all
# the versions of this secret.
print("\n.. List versions of the secret using its name")
secret_versions = client.list_properties_of_secret_versions(bank_secret.name)
for secret_version in secret_versions:
    print(
        "Bank Secret with name '{0}' has version: '{1}'.".format(
            secret_version.name, secret_version.version
        )
    )

# The bank account and storage accounts got closed. Let's delete bank and storage accounts secrets.
# Calling result() on the method will immediately return the `DeletedSecret`, but calling wait() blocks
# until the secret is deleted server-side.
print("\n.. Deleting secrets...")
client.begin_delete_secret(bank_secret.name).wait()
client.begin_delete_secret(storage_secret.name).wait()


# You can list all the deleted and non-purged secrets, assuming Key Vault is soft-delete enabled.
print("\n.. List deleted secrets from the Key Vault")
deleted_secrets = client.list_deleted_secrets()
for deleted_secret in deleted_secrets:
    print(
        "Secret with name '{0}' has recovery id '{1}'".format(deleted_secret.name, deleted_secret.recovery_id)
    )
