import time
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
# Sample - demonstrates the basic backup and restore operations on a vault(secret) resource for Azure Key Vault
#
# 1. Create a secret (set_secret)
#
# 2. Backup a secret (backup_secret)
#
# 3. Delete a secret (delete_secret)
#
# 4. Restore a secret (restore_secret)
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
        # Let's create a secret holding storage account credentials.
        # if the secret already exists in the Key Vault, then a new version of the secret is created.
        print("\n1. Create Secret")
        secret = client.set_secret("backupRestoreSecretName", "backupRestoreSecretValue")
        print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))

        # Backups are good to have, if in case secrets gets deleted accidentally.
        # For long term storage, it is ideal to write the backup to a file.
        print("\n2. Create a backup for an existing Secret")
        secret_backup = client.backup_secret(secret.name)
        print("Backup created for secret with name '{0}'.".format(secret.name))

        # The storage account secret is no longer in use, so you delete it.
        client.delete_secret(secret.name)

        # To ensure secret is deleted on the server side.
        print("\nDeleting secret...")
        time.sleep(20)
        print("Deleted Secret with name '{0}'".format(secret.name))

        # In future, if the secret is required again, we can use the backup value to restore it in the Key Vault.
        print("\n3. Restore the secret using the backed up secret bytes")
        secret = client.restore_secret(secret_backup)
        print("Restored Secret with name '{0}'".format(secret.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        run_sample()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
