import asyncio
import os
from azure.keyvault.keys.aio import KeyClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
# 2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-keys/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic recover and purge operations on a vault(key) resource for Azure Key Vault. The vault has to be soft-delete enabled to perform the following operations. [Azure Key Vault soft delete](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete)
#
# 1. Create a key (create_key)
#
# 2. Delete a key (delete_key)
#
# 3. Recover a deleted key (recover_deleted_key)
#
# 4. Purge a deleted key (purge_deleted_key)
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
        # Let's create keys with RSA and EC type. If the key
        # already exists in the Key Vault, then a new version of the key is created.
        print("\n1. Create Key")
        rsa_key = await client.create_rsa_key("rsaKeyName", hsm=False)
        ec_key = await client.create_ec_key("ecKeyName", hsm=False)
        print("Key with name '{0}' was created of type '{1}'.".format(rsa_key.name, rsa_key.key_material.kty))
        print("Key with name '{0}' was created of type '{1}'.".format(ec_key.name, ec_key.key_material.kty))

        # The ec key is no longer needed. Need to delete it from the Key Vault.
        print("\n2. Delete a Key")
        key = await client.delete_key(rsa_key.name)
        await asyncio.sleep(30)
        print("Key with name '{0}' was deleted on date {1}.".format(key.name, key.deleted_date))

        # We accidentally deleted the rsa key. Let's recover it.
        # A deleted key can only be recovered if the Key Vault is soft-delete enabled.
        print("\n3. Recover Deleted  Key")
        recovered_key = await client.recover_deleted_key(rsa_key.name)
        print("Recovered Key with name '{0}'.".format(recovered_key.name))

        # Let's delete ec key now.
        # If the keyvault is soft-delete enabled, then for permanent deletion deleted key needs to be purged.
        await client.delete_key(ec_key.name)

        # To ensure key is deleted on the server side.
        print("\nDeleting EC Key...")
        await asyncio.sleep(20)

        # To ensure permanent deletion, we might need to purge the key.
        print("\n4. Purge Deleted Key")
        await client.purge_deleted_key(ec_key.name)
        print("EC Key has been permanently deleted.")

    except HttpResponseError as e:
        if "(NotSupported)" in e.message:
            print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
        else:
            print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
