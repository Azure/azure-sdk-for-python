# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class KeyVaultSecrets:
    def __init__(self):
        # DefaultAzureCredential() expects the following environment variables:
        # * AZURE_CLIENT_ID
        # * AZURE_CLIENT_SECRET
        # * AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url=os.environ["AZURE_PROJECT_URL"], credential=credential
        )

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
        deleted_secret = self.secret_client.delete_secret(self.secret_name)
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
