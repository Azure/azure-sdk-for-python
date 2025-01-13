# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import datetime
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://learn.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, get, update, and delete permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a vault(key) resource for Azure Key Vault
#
# 1. Create a new RSA Key (create_rsa_key)
#
# 2. Create a new EC Key (create_ec_key)
#
# 3. Get an existing key (get_key)
#
# 4. Update an existing key's properties (update_key_properties)
#
# 5. Delete a key (delete_key)
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a key client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)

    # Let's create an RSA key with size 2048, hsm disabled and optional key_operations of encrypt, decrypt.
    # if the key already exists in the Key Vault, then a new version of the key is created.
    print("\n.. Create an RSA Key")
    key_size = 2048
    key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
    key_name = "rsaKeyNameAsync"
    rsa_key = await client.create_rsa_key(key_name, size=key_size, key_operations=key_ops)
    print(f"RSA Key with name '{rsa_key.name}' created of type '{rsa_key.key_type}'.")

    # Let's create an Elliptic Curve key with algorithm curve type P-256.
    # if the key already exists in the Key Vault, then a new version of the key is created.
    print("\n.. Create an EC Key")
    key_curve = "P-256"
    key_name = "ECKeyNameAsync"
    ec_key = await client.create_ec_key(key_name, curve=key_curve)
    print(f"EC Key with name '{ec_key.name}' created of type {ec_key.key_type}.")

    # Let's get the rsa key details using its name
    print("\n.. Get a Key using it's name")
    rsa_key = await client.get_key(rsa_key.name)
    print(f"Key with name '{rsa_key.name}' was found.")

    # Let's say we want to update the expiration time for the EC key and disable the key to be usable
    # for cryptographic operations. The update method allows the user to modify the metadata (key attributes)
    # associated with a key previously stored within Key Vault.
    print("\n.. Update a Key by name")
    expires_on = datetime.datetime.utcnow() + datetime.timedelta(days=365)
    updated_ec_key = await client.update_key_properties(
        ec_key.name, version=ec_key.properties.version, expires_on=expires_on, enabled=False
    )
    print(f"Key with name '{updated_ec_key.name}' was updated on date '{updated_ec_key.properties.updated_on}'")
    print(f"Key with name '{updated_ec_key.name}' was updated to expire on '{updated_ec_key.properties.expires_on}'")

    # The keys are no longer used, let's delete them
    print("\n.. Deleting keys")
    for key_name in (ec_key.name, rsa_key.name):
        deleted_key = await client.delete_key(key_name)
        print(f"\nDeleted '{deleted_key.name}'")

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
