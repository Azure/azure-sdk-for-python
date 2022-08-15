# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
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
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, delete, recover, and purge permissions for your service principal in your vault
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates deleting and purging keys
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
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)

print("\n.. Create keys")
rsa_key = client.create_rsa_key("rsaKeyName")
ec_key = client.create_ec_key("ecKeyName")
print("Created key '{0}' of type '{1}'.".format(rsa_key.name, rsa_key.key_type))
print("Created key '{0}' of type '{1}'.".format(ec_key.name, ec_key.key_type))

print("\n.. Delete the keys")
for key_name in (ec_key.name, rsa_key.name):
    client.begin_delete_key(key_name).wait()
    print("Deleted key '{0}'".format(key_name))

# A deleted key can only be recovered if the Key Vault is soft-delete enabled.
print("\n.. Recover a deleted key")
recover_key_poller = client.begin_recover_deleted_key(rsa_key.name)
recovered_key = recover_key_poller.result()

# This wait is just to ensure recovery is complete before we delete the key again
recover_key_poller.wait()
print("Recovered key '{0}'".format(recovered_key.name))

# To permanently delete the key, the deleted key needs to be purged.
# Calling result() on the method will immediately return the `DeletedKey`, but calling wait() blocks
# until the key is deleted server-side so it can be purged.
client.begin_delete_key(recovered_key.name).wait()

# Keys will still purge eventually on their scheduled purge date, but calling `purge_deleted_key` immediately
# purges.
print("\n.. Purge keys")
for key_name in (ec_key.name, rsa_key.name):
    client.purge_deleted_key(key_name)
    print("Purged '{}'".format(key_name))
