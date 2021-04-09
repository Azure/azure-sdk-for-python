# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid
from azure.keyvault.secrets import SecretClient
from key_vault_base import KeyVaultBase


class KeyVaultSecrets(KeyVaultBase):
    def __init__(self):
        args = self.get_client_args()
        self.secret_client = SecretClient(**args)
        self.secret_name = "secret-name-" + uuid.uuid1().hex
        self.secret_Value = "secret-value"

    def set_secret(self):
        print("Setting a secret...")
        self.secret_client.set_secret(self.secret_name, self.secret_Value)
        print("\tdone")

    def get_secret(self):
        print("Getting a secret...")
        secret = self.secret_client.get_secret(self.secret_name)
        print("\tdone, secret: (" + secret.name + "," + secret.value + ").")

    def delete_secret(self):
        print("Deleting a secret...")
        deleted_secret = self.secret_client.begin_delete_secret(self.secret_name).result()
        print("\tdone: " + deleted_secret.name)

    def run(self):
        print("")
        print("------------------------")
        print("Key Vault - Secrets\nIdentity - Credential")
        print("------------------------")
        print("1) Set a secret")
        print("2) Get that secret")
        print("3) Delete that secret (Clean up the resource)")
        print("")

        try:
            self.set_secret()
            self.get_secret()
        finally:
            self.delete_secret()