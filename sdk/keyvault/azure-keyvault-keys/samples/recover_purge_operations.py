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
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_ENDPOINT
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic list operations on a vault(key) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. See
# https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete for more information about soft-delete.
#
# 1. Create a key (create_key)
#
# 2. Delete a key (begin_delete_key)
#
# 3. Recover a deleted key (begin_recover_deleted_key)
#
# 4. Purge a deleted key (purge_deleted_key)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a key client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_ENDPOINT = os.environ["VAULT_ENDPOINT"]
credential = DefaultAzureCredential()
client = KeyClient(vault_endpoint=VAULT_ENDPOINT, credential=credential)
try:
    print("\n.. Create keys")
    rsa_key = client.create_rsa_key("rsaKeyName")
    ec_key = client.create_ec_key("ecKeyName")
    print("Created key '{0}' of type '{1}'.".format(rsa_key.name, rsa_key.key_type))
    print("Created key '{0}' of type '{1}'.".format(ec_key.name, ec_key.key_type))

    print("\n.. Delete the keys")
    for key_name in (ec_key.name, rsa_key.name):
        deleted_key = client.begin_delete_key(key_name).result()
        print("Deleted key '{0}'".format(deleted_key.name))

    print("\n.. Recover a deleted key")
    recovered_key = client.begin_recover_deleted_key(rsa_key.name).result()
    print("Recovered key '{0}'".format(recovered_key.name))

    # deleting the recovered key so it doesn't outlast this script
    client.begin_delete_key(recovered_key.name).wait()

    print("\n.. Purge keys")
    for key_name in (ec_key.name, rsa_key.name):
        client.purge_deleted_key(key_name)
        print("Purged '{}'".format(key_name))

except HttpResponseError as e:
    if "(NotSupported)" in e.message:
        print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
    else:
        print("\nrun_sample has caught an error. {0}".format(e.message))

finally:
    print("\nrun_sample done")
