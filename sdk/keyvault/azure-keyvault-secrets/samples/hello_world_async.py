# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import os
import asyncio
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
# Sample - demonstrates the basic CRUD operations on a vault(secret) resource for Azure Key Vault
#
# 1. Create a new secret (set_secret)
#
# 2. Get an existing secret (get_secret)
#
# 3. Update an existing secret's properties (update_secret_properties)
#
# 4. Delete a secret (delete_secret)
#
# ----------------------------------------------------------------------------------------------------------
async def run_sample():
    # Instantiate a secret client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=VAULT_URL, credential=credential)

    # Let's create a secret holding bank account credentials valid for 1 year.
    # if the secret already exists in the key vault, then a new version of the secret is created.
    print("\n.. Create Secret")
    expires_on = datetime.datetime.utcnow() + datetime.timedelta(days=365)
    secret = await client.set_secret("helloWorldSecretNameAsync", "helloWorldSecretValue", expires_on=expires_on)
    print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))
    print("Secret with name '{0}' expires on '{1}'".format(secret.name, secret.properties.expires_on))

    # Let's get the bank secret using its name
    print("\n.. Get a Secret by name")
    bank_secret = await client.get_secret(secret.name)
    print("Secret with name '{0}' was found with value '{1}'.".format(bank_secret.name, bank_secret.value))

    # After one year, the bank account is still active, we need to update the expiry time of the secret.
    # The update method can be used to update the expiry attribute of the secret. It cannot be used to update
    # the value of the secret.
    print("\n.. Update a Secret by name")
    expires_on = bank_secret.properties.expires_on + datetime.timedelta(days=365)
    updated_secret_properties = await client.update_secret_properties(secret.name, expires_on=expires_on)
    print(
        "Secret with name '{0}' was updated on date '{1}'".format(
            updated_secret_properties.name, updated_secret_properties.updated_on
        )
    )
    print(
        "Secret with name '{0}' was updated to expire on '{1}'".format(
            updated_secret_properties.name, updated_secret_properties.expires_on
        )
    )

    # Bank forced a password update for security purposes. Let's change the value of the secret in the key vault.
    # To achieve this, we need to create a new version of the secret in the key vault. The update operation cannot
    # change the value of the secret.
    new_secret = await client.set_secret(secret.name, "newSecretValueAsync")
    print("Secret with name '{0}' created with value '{1}'".format(new_secret.name, new_secret.value))

    # The bank account was closed, need to delete its credentials from the Key Vault.
    print("\n.. Deleting Secret...")
    deleted_secret = await client.delete_secret(secret.name)
    print("Secret with name '{0}' was deleted.".format(deleted_secret.name))

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
