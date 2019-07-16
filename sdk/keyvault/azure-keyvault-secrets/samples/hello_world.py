import datetime
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-secrets/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a vault(secret) resource for Azure Key Vault
#
# 1. Create a new Secret (set_secret)
#
# 2. Get an existing secret (get_secret)
#
# 3. Update an existing secret (set_secret)
#
# 4. Delete a secret (delete_secret)
#
# ----------------------------------------------------------------------------------------------------------
def run_sample():
    # Instantiate a secret client that will be used to call the service.
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)
    try:
        # Let's create a secret holding bank account credentials valid for 1 year.
        # if the secret already exists in the Key Vault, then a new version of the secret is created.
        print("\n1. Create Secret")
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        secret = client.set_secret("helloWorldSecretName", "helloWorldSecretValue", expires=expires)
        print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))
        print("Secret with name '{0}' expires on '{1}'".format(secret.name, secret.expires))

        # Let's get the bank secret using its name
        print("\n2. Get a Secret by name")
        bank_secret = client.get_secret(secret.name)
        print("Secret with name '{0}' was found with value '{1}'.".format(bank_secret.name, bank_secret.value))

        # After one year, the bank account is still active, we need to update the expiry time of the secret.
        # The update method can be used to update the expiry attribute of the secret. It cannot be used to update
        # the value of the secret.
        print("\n3. Update a Secret by name")
        expires = bank_secret.expires + datetime.timedelta(days=365)
        updated_secret = client.update_secret(secret.name, expires=expires)
        print("Secret with name '{0}' was updated on date '{1}'".format(secret.name, updated_secret.updated))
        print("Secret with name '{0}' was updated to expire on '{1}'".format(secret.name, updated_secret.expires))

        # Bank forced a password update for security purposes. Let's change the value of the secret in the Key Vault.
        # To achieve this, we need to create a new version of the secret in the Key Vault. The update operation cannot
        # change the value of the secret.
        secret = client.set_secret(secret.name, "newSecretValue")
        print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))

        # The bank account was closed, need to delete its credentials from the Key Vault.
        print("\n4. Delete Secret")
        deleted_secret = client.delete_secret(secret.name)
        print("Deleting Secret..")
        print("Secret with name '{0}' was deleted.".format(deleted_secret.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        run_sample()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
