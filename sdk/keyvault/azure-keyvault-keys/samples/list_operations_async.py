# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, list, and delete permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic list operations for keys
#
# 1. Create a key (create_key)
#
# 2. List keys from the Key Vault (list_keys)
#
# 3. List key versions from the Key Vault (list_properties_of_key_versions)
#
# 4. Delete keys (delete_key)
#
# 5. List deleted keys from the Key Vault (list_deleted_keys)
#
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)

    # Let's create keys with RSA and EC type. If the key
    # already exists in the Key Vault, then a new version of the key is created.
    print("\n.. Create Key")
    rsa_key = await client.create_rsa_key("rsaKeyNameAsync")
    ec_key = await client.create_ec_key("ecKeyNameAsync")
    print("Key with name '{0}' was created of type '{1}'.".format(rsa_key.name, rsa_key.key_type))
    print("Key with name '{0}' was created of type '{1}'.".format(ec_key.name, ec_key.key_type))

    # You need to check the type of all the keys in the vault.
    # Let's list the keys and print their key types.
    # List operations don 't return the keys with their type information.
    # So, for each returned key we call get_key to get the key with its type information.
    print("\n.. List keys from the Key Vault")
    keys = client.list_properties_of_keys()
    async for key in keys:
        retrieved_key = await client.get_key(key.name)
        print(
            "Key with name '{0}' with type '{1}' was found.".format(
                retrieved_key.name, retrieved_key.key_type
            )
        )

    # The rsa key size now should now be 3072, default - 2048. So you want to update the key in Key Vault to ensure
    # it reflects the new key size. Calling create_rsa_key on an existing key creates a new version of the key in
    # the Key Vault with the new key size.
    new_key = await client.create_rsa_key(rsa_key.name, size=3072)
    print("New version was created for Key with name '{0}' with the updated size.".format(new_key.name))

    # You should have more than one version of the rsa key at this time. Lets print all the versions of this key.
    print("\n.. List versions of the key using its name")
    key_versions = client.list_properties_of_key_versions(rsa_key.name)
    async for key in key_versions:
        print("RSA Key with name '{0}' has version: '{1}'".format(key.name, key.version))

    # Both the rsa key and ec key are not needed anymore. Let's delete those keys.
    print("\n..Deleting keys...")
    await client.delete_key(rsa_key.name)
    await client.delete_key(ec_key.name)

    # You can list all the deleted and non-purged keys.
    print("\n.. List deleted keys from the Key Vault")
    deleted_keys = client.list_deleted_keys()
    async for deleted_key in deleted_keys:
        print("Key with name '{0}' has recovery id '{1}'".format(deleted_key.name, deleted_key.recovery_id))

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
