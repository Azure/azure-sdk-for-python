# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import asyncio
import os
from azure.keyvault.keys.aio import KeyClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
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
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = KeyClient(vault_url=VAULT_URL, credential=credential)
    try:
        # Let's create an RSA key with size 2048, hsm disabled and optional key_operations of encrypt, decrypt.
        # if the key already exists in the Key Vault, then a new version of the key is created.
        print("\n.. Create an RSA Key")
        key_size = 2048
        key_ops = ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
        key_name = "rsaKeyName"
        rsa_key = await client.create_rsa_key(key_name, size=key_size, key_operations=key_ops)
        print("RSA Key with name '{0}' created of type '{1}'.".format(rsa_key.name, rsa_key.key_type))

        # Let's create an Elliptic Curve key with algorithm curve type P-256.
        # if the key already exists in the Key Vault, then a new version of the key is created.
        print("\n.. Create an EC Key")
        key_curve = "P-256"
        key_name = "ECKeyName"
        ec_key = await client.create_ec_key(key_name, curve=key_curve)
        print("EC Key with name '{0}' created of type {1}.".format(ec_key.name, ec_key.key_type))

        # Let's get the rsa key details using its name
        print("\n.. Get a Key using it's name")
        rsa_key = await client.get_key(rsa_key.name)
        print("Key with name '{0}' was found.".format(rsa_key.name))

        # Let's say we want to update the expiration time for the EC key and disable the key to be usable
        # for cryptographic operations. The update method allows the user to modify the metadata (key attributes)
        # associated with a key previously stored within Key Vault.
        print("\n.. Update a Key by name")
        expires_on = datetime.datetime.utcnow() + datetime.timedelta(days=365)
        updated_ec_key = await client.update_key_properties(
            ec_key.name, version=ec_key.properties.version, expires_on=expires_on, enabled=False
        )
        print(
            "Key with name '{0}' was updated on date '{1}'".format(
                updated_ec_key.name, updated_ec_key.properties.updated_on
            )
        )
        print(
            "Key with name '{0}' was updated to expire on '{1}'".format(
                updated_ec_key.name, updated_ec_key.properties.expires_on
            )
        )

        # The keys are no longer used, let's delete them
        print("\n.. Deleting keys")
        for key_name in (ec_key.name, rsa_key.name):
            deleted_key = await client.delete_key(key_name)
            print("\nDeleted '{}'".format(deleted_key.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")
        await credential.close()
        await client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
