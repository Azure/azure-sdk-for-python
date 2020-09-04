# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid
from azure.keyvault.secrets.aio import SecretClient
from key_vault_base_async import KeyVaultBaseAsync


class KeyVaultSecrets(KeyVaultBaseAsync):
    def __init__(self):
        args = self.get_client_args()
        self.secret_client = SecretClient(**args)
        self.secret_name = "secret-name-" + uuid.uuid1().hex
        self.secret_value = "secret-value"

    async def set_secret(self):
        print("Setting a secret...")
        secret = await self.secret_client.set_secret(
            self.secret_name, self.secret_value
        )
        print("\tdone, secret: (" + secret.name + "," + secret.value + ").")

    async def get_secret(self):
        print("Getting a secret...")
        secret = await self.secret_client.get_secret(self.secret_name)
        print("\tdone, secret: (" + secret.name + "," + secret.value + ").")

    async def delete_secret(self):
        print("Deleting a secret...")
        await self.secret_client.delete_secret(self.secret_name)
        print("\tdone")

    async def run(self):

        print("")
        print("------------------------")
        print("Key Vault - Secrets\nIdentity - Credential")
        print("------------------------")
        print("1) Set a secret")
        print("2) Get that secret")
        print("3) Delete that secret (Clean up the resource)")
        print("")

        try:
            await self.set_secret()
            await self.get_secret()
        finally:
            await self.delete_secret()
