# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates import CertificatePolicy
from azure.keyvault.certificates.aio import CertificateClient

class KeyVaultCertificates:
    def __init__(self):
        # DefaultAzureCredential() expects the following environment variables:
        # * AZURE_CLIENT_ID
        # * AZURE_CLIENT_SECRET
        # * AZURE_TENANT_ID
        credential = DefaultAzureCredential()
        self.certificate_client = CertificateClient(
            vault_url=os.environ["AZURE_PROJECT_URL"], credential=credential
        )

        self.certificate_name = "cert-name-" + uuid.uuid1().hex

    async def create_certificate(self):
        await self.certificate_client.create_certificate(
            certificate_name=self.certificate_name, policy=CertificatePolicy.get_default())
        print("\tdone")

    async def get_certificate(self):
        print("Getting a certificate...")
        certificate = await self.certificate_client.get_certificate(certificate_name=self.certificate_name)
        print("\tdone, certificate: {}.".format(certificate.name))

    async def delete_certificate(self):
        print("Deleting a certificate...")
        deleted_certificate = await self.certificate_client.delete_certificate(certificate_name=self.certificate_name)
        print("\tdone: " + deleted_certificate.name)

    async def run(self):
        print("")
        print("------------------------")
        print("Key Vault - Certificates\nIdentity - Credential")
        print("------------------------")
        print("1) Create a certificate")
        print("2) Get that certificate")
        print("3) Delete that certificate (Clean up the resource)")
        print("")

        try:
            await self.create_certificate()
            await self.get_certificate()
        finally:
            await self.delete_certificate()