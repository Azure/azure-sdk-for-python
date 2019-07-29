import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient


class KeyVault_async:
    def __init__(self):
        # DefaultAzureCredential() expects the following environment variables:
        # * AZURE_CLIENT_ID
        # * AZURE_CLIENT_SECRET
        # * AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        self.secret_client = SecretClient(
            vault_url=os.environ["AZURE_PROJECT_URL"], credential=credential
        )
        self.secret_name = "MySecret"
        self.secret_value = "My Secret Value"

    async def SetSecret(self):
        print("Setting a secret...")
        secret = await self.secret_client.set_secret(
            self.secret_name, self.secret_value
        )
        print("\tdone, secret: (" + secret.name + "," + secret.value + ").")

    async def GetSecret(self):
        print("Getting a secret...")
        secret = await self.secret_client.get_secret(self.secret_name)
        print("\tdone, secret: (" + secret.name + "," + secret.value + ").")

    async def DeleteSecret(self):
        print("Deleting a secret...")
        await self.secret_client.delete_secret(self.secret_name)
        print("\tdone")

    async def Run(self):

        print("")
        print("------------------------")
        print("Key Vault - Secrets\nIdentity - Credential")
        print("------------------------")
        print("1) Set a secret")
        print("2) Get that secret")
        print("3) Delete that secret (Clean up the resource)")
        print("")

        try:
            await self.SetSecret()
            await self.GetSecret()
        finally:
            await self.DeleteSecret()
