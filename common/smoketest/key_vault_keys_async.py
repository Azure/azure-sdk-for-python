# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys.aio import KeyClient


class KeyVaultKeys:
    def __init__(self):
        # DefaultAzureCredential() expects the following environment variables:
        # * AZURE_CLIENT_ID
        # * AZURE_CLIENT_SECRET
        # * AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        self.key_client = KeyClient(
            vault_url=os.environ["AZURE_PROJECT_URL"], credential=credential
        )

        self.key_name = "key-name-" + uuid.uuid1().hex

    async def create_rsa_key(self):
        print("Creating an RSA key...")
        await self.key_client.create_rsa_key(name=self.key_name, size=2048, hsm=False)
        print("\tdone")

    async def get_key(self):
        print("Getting a key...")
        key = await self.key_client.get_key(name=self.key_name)
        print(f"\tdone, key: {key.name}.")

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
