# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import uuid
from azure.keyvault.keys import KeyClient
from key_vault_base import KeyVaultBase


class KeyVaultKeys(KeyVaultBase):
    def __init__(self):
        args = self.get_client_args()
        self.key_client = KeyClient(**args)
        self.key_name = "key-name-" + uuid.uuid1().hex

    def create_rsa_key(self):
        print("Creating an RSA key...")
        self.key_client.create_rsa_key(name=self.key_name, size=2048)
        print("\tdone")

    def get_key(self):
        print("Getting a key...")
        key = self.key_client.get_key(name=self.key_name)
        print("\tdone, key: {}.".format(key.name))

    def delete_key(self):
        print("Deleting a key...")
        deleted_key = self.key_client.begin_delete_key(name=self.key_name).result()
        print("\tdone: " + deleted_key.name)

    def run(self):
        print("")
        print("------------------------")
        print("Key Vault - Keys\nIdentity - Credential")
        print("------------------------")
        print("1) Create a key")
        print("2) Get that key")
        print("3) Delete that key (Clean up the resource)")
        print("")

        try:
            self.create_rsa_key()
            self.get_key()
        finally:
            self.delete_key()