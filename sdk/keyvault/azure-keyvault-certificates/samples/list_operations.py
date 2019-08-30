# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import time
import os
from azure.keyvault.certificates import CertificateClient, CertificatePolicy, KeyProperties, SecretContentType
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
# 2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-certificates/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic list operations on a vault(certificate) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations. [Azure Key Vault soft delete]
# (https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete)
#
# 1. Create certificate (create_certificate)
#
# 2. List certificates from the Key Vault (list_certificates)
#
# 3. List certificate versions from the Key Vault (list_certificate_versions)
#
# 4. List deleted certificates from the Key Vault (list_deleted_certificates). The vault has to be soft-delete enabled
# to perform this operation.
#
# ----------------------------------------------------------------------------------------------------------

def run_sample():
    # Instantiate a certificate client that will be used to call the service. Notice that the client is using default
    # Azure credentials. To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=VAULT_URL, credential=credential)
    try:
        # Let's create a certificate for holding storage and bank accounts credentials. If the certificate
        # already exists in the Key Vault, then a new version of the certificate is created.
        print("\n1. Create Certificate")
        bank_cert_name = "BankListCertificate"
        storage_cert_name = "StorageListCertificate"
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)

        bank_certificate_poller = client.create_certificate(name=bank_cert_name, expires=expires)
        storage_certificate_poller = client.create_certificate(name=storage_cert_name)

        # await the creation of the bank and storage certificate
        bank_certificate_poller.wait()
        storage_certificate_poller.wait()

        print("Certificate with name '{0}' was created.".format(bank_cert_name))
        print("Certificate with name '{0}' was created.".format(storage_cert_name))

        # Let's list the certificates.
        print("\n2. List certificates from the Key Vault")
        certificates = client.list_certificates()
        for certificate in certificates:
            print("Certificate with name '{0}' was found.".format(certificate.name))

        # You find the bank certificate needs to change the expiration date because the bank account credentials will be
        # valid for an extra year. Calling create_certificate on an existing certificate creates a new version of the
        # certificate in the Key Vault with the new value.

        expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)

        client.create_certificate(
            name=bank_cert_name,
            policy=cert_policy,
            expires=expires
        ).wait()
        print(
            "Certificate with name '{0}' was updated with expiration date '{1}'".format(
                bank_cert_name,
                expires
            )
        )

        # You need to check all the different expiration dates your bank account certificate had previously. Let's print
        # all the versions of this certificate.
        print("\n3. List versions of the certificate using its name")
        certificate_versions = client.list_certificate_versions(bank_cert_name)
        for certificate_version in certificate_versions:
            print("Bank Certificate with name '{0}' with version '{1}' has expiration date: '{2}'.".format(
                certificate_version.name,
                certificate_version.version,
                certificate_version.expires))

        # The bank acoount and storage accounts got closed. Let's delete bank and storage accounts certificates.
        client.delete_certificate(name=bank_cert_name)
        client.delete_certificate(name=storage_cert_name)

        # You can list all the deleted and non-purged certificates, assuming Key Vault is soft-delete enabled.
        print("\n3. List deleted certificates from the Key Vault")
        deleted_certificates = client.list_deleted_certificates()
        for deleted_certificate in deleted_certificates:
            print("Certificate with name '{0}' has recovery id '{1}'".format(
                    deleted_certificate.name,
                    deleted_certificate.recovery_id))

    except HttpResponseError as e:
        if "(NotSupported)" in e.message:
            print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
        else:
            print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        run_sample()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
