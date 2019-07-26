import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class KeyVault:
    def __init__(self):
        # DefaultAzureCredential() expects the following environment variables:
        # * AZURE_CLIENT_ID
        # * AZURE_CLIENT_SECRET
        # * AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url=os.environ["AZURE_PROJECT_URL"], credential=credential
        )

    def SetSecret(self):
        print("Setting a secret...")
        self.secret_client.set_secret("secret-name", "secret-value")
        print("\tdone")

    def GetSecret(self):
        print("Getting a secret...")
        secret = self.secret_client.get_secret("secret-name")
        print("\tdone: " + secret.name)

    def DeleteSecret(self):
        print("Deleting a secret...")
        deleted_secret = self.secret_client.delete_secret("secret-name")
        print("\tdone: " + deleted_secret.name)

    def Run(self):
        print()
        print("------------------------")
        print("Key Vault - Secrets\nIdentity - Credential")
        print("------------------------")
        print("1) Set a secret")
        print("2) Get that secret")
        print("3) Delete that secret (Clean up the resource)")
        print()

        try:
            self.SetSecret()
            self.GetSecret()
        finally:
            self.DeleteSecret()
