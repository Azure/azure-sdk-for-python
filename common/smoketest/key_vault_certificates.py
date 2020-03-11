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
        print("Creating certificate (name: {})".format(self.certificate_name))
        create_poller = self.certificate_client.begin_create_certificate(
            certificate_name=self.certificate_name,
            policy=CertificatePolicy.get_default())
        print("\twaiting...")
        create_poller.result()
        print("\tdone")

    def get_certificate(self):
        print("Getting a certificate...")
        certificate = self.certificate_client.get_certificate(certificate_name=self.certificate_name)
        print("\tdone, certificate: {}.".format(certificate.name))

    def delete_certificate(self):
        print("Deleting a certificate...")
        poller = self.certificate_client.begin_delete_certificate(certificate_name=self.certificate_name)
        deleted_certificate = poller.result()
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