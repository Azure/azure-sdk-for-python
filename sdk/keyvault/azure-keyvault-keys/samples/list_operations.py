# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
import os
from azure.keyvault.keys import KeyClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-keys/
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic list operations on a vault(key) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
#
# 1. Create key (create_key)
#
# 2. List keys from the Key Vault (list_keys)
#
# 3. List key versions from the Key Vault (list_properties_of_key_versions)
#
# 4. List deleted keys from the Key Vault (list_deleted_keys). The vault has to be soft-delete enabled to perform this
# operation.
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a key client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)
try:
    # Let's create keys with RSA and EC type. If the key
    # already exists in the Key Vault, then a new version of the key is created.
    print("\n.. Create Key")
    rsa_key = client.create_rsa_key("rsaKeyName")
    ec_key = client.create_ec_key("ecKeyName")
    print("Key with name '{0}' was created of type '{1}'.".format(rsa_key.name, rsa_key.key_type))
    print("Key with name '{0}' was created of type '{1}'.".format(ec_key.name, ec_key.key_type))

    # You need to check the type of all the keys in the vault.
    # Let's list the keys and print their key types.
    # List operations don 't return the keys with their type information.
    # So, for each returned key we call get_key to get the key with its type information.
    print("\n.. List keys from the Key Vault")
    keys = client.list_properties_of_keys()
    for key in keys:
        retrieved_key = client.get_key(key.name)
        print(
            "Key with name '{0}' with type '{1}' was found.".format(retrieved_key.name, retrieved_key.key_type)
        )

    # The rsa key size now should now be 3072, default - 2048. So you want to update the key in Key Vault to ensure
    # it reflects the new key size. Calling create_rsa_key on an existing key creates a new version of the key in
    # the Key Vault with the new key size.
    new_key = client.create_rsa_key(rsa_key.name, size=3072)
    print("New version was created for Key with name '{0}' with the updated size.".format(new_key.name))

    # You should have more than one version of the rsa key at this time. Lets print all the versions of this key.
    print("\n.. List versions of a key using its name")
    key_versions = client.list_properties_of_key_versions(rsa_key.name)
    for key in key_versions:
        print("Key '{0}' has version: '{1}'".format(key.name, key.version))

    # Both the rsa key and ec key are not needed anymore. Let's delete those keys.
    print("\n.. Delete the created keys...")
    for key_name in (ec_key.name, rsa_key.name):
        client.begin_delete_key(key_name).wait()

    # You can list all the deleted and non-purged keys, assuming Key Vault is soft-delete enabled.
    print("\n.. List deleted keys from the Key Vault (requires soft-delete)")
    deleted_keys = client.list_deleted_keys()
    for deleted_key in deleted_keys:
        print("Key with name '{0}' has recovery id '{1}'".format(deleted_key.name, deleted_key.recovery_id))

except HttpResponseError as e:
    if "(NotSupported)" in e.message:
        print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
    else:
        print("\nThis sample has caught an error. {0}".format(e.message))
