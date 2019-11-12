# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy


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

    def create_certificate(self):
        print("creating certificate...")
        self.certificate_client.create_certificate(name=self.certificate_name)
        print("\tdone")

    def get_certificate(self):
        print("Getting a certificate...")
        certificate = self.certificate_client.get_certificate_with_policy(name=self.certificate_name)
        print("\tdone, certificate: %s." % certificate.name)

    def delete_certificate(self):
        print("Deleting a certificate...")
        deleted_certificate = self.certificate_client.delete_certificate(name=self.certificate_name)
        print("\tdone: " + deleted_certificate.name)

    def run(self):
        print("")
        print("------------------------")
        print("Key Vault - Certificates\nIdentity - Credential")
        print("------------------------")
        print("1) Create a certificate")
        print("2) Get that certificate")
        print("3) Delete that certificate (Clean up the resource)")
        print("")

        try:
            self.create_certificate()
            self.get_certificate()
        finally:
            self.delete_certificate()
