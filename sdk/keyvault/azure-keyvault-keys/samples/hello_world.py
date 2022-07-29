# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your key vault
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
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
# 4. Update an existing key (update_key)
#
# 5. Delete a key (begin_delete_key)
# ----------------------------------------------------------------------------------------------------------

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
key_name = "rsaKeyName"
rsa_key = client.create_rsa_key(key_name, size=key_size, key_operations=key_ops)
print(f"RSA Key with name '{rsa_key.name}' created of type '{rsa_key.key_type}'")

# Let's create an Elliptic Curve key with algorithm curve type P-256.
# if the key already exists in the Key Vault, then a new version of the key is created.
print("\n.. Create an EC Key")
key_curve = "P-256"
key_name = "ECKeyName"
ec_key = client.create_ec_key(key_name, curve=key_curve)
print(f"EC Key with name '{ec_key.name}' created of type '{ec_key.key_type}'")

# Let's get the rsa key details using its name
print("\n.. Get a Key by its name")
rsa_key = client.get_key(rsa_key.name)
print(f"Key with name '{rsa_key.name}' was found.")

# Let's say we want to update the expiration time for the EC key and disable the key to be usable
# for cryptographic operations. The update method allows the user to modify the metadata (key attributes)
# associated with a key previously stored within Key Vault.
print("\n.. Update a Key by name")
expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
updated_ec_key = client.update_key_properties(
    ec_key.name, ec_key.properties.version, expires_on=expires, enabled=False
)
print(
    f"Key with name '{updated_ec_key.name}' was updated on date '{updated_ec_key.properties.updated_on}'"
)
print(
    f"Key with name '{updated_ec_key.name}' was updated to expire on '{updated_ec_key.properties.expires_on}'"
)

# The RSA key is no longer used, need to delete it from the Key Vault.
print("\n.. Delete Keys")
client.begin_delete_key(ec_key.name)
client.begin_delete_key(rsa_key.name)
print(f"Deleted key '{ec_key.name}'")
print(f"Deleted key '{rsa_key.name}'")
