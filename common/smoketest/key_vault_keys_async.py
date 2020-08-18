# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid
from azure.keyvault.keys.aio import KeyClient
from key_vault_base_async import KeyVaultBaseAsync


class KeyVaultKeys(KeyVaultBaseAsync):
    def __init__(self):
        args = self.get_client_args()
        self.key_client = KeyClient(**args)
        self.key_name = "key-name-" + uuid.uuid1().hex

    async def create_rsa_key(self):
        print("Creating an RSA key...")
        await self.key_client.create_rsa_key(name=self.key_name, size=2048)
        print("\tdone")

    async def get_key(self):
        print("Getting a key...")
        key = await self.key_client.get_key(name=self.key_name)
        print("\tdone, key: {}.".format(key.name))

    async def delete_key(self):
        print("Deleting a key...")
        deleted_key = await self.key_client.delete_key(name=self.key_name)
        print("\tdone: " + deleted_key.name)

    async def run(self):

        print("")
        print("------------------------")
        print("Key Vault - Keys\nIdentity - Credential")
        print("------------------------")
        print("1) Create a key")
        print("2) Get that key")
        print("3) Delete that key (Clean up the resource)")
        print("")

        try:
            await self.create_rsa_key()
            await self.get_key()
        finally:
            await self.delete_key()