# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic recover and purge operations on a vault(certificate) resource for Azure Key Vault
#
# 1. Create a certificate (begin_create_certificate)
#
# 2. Delete a certificate (begin_delete_certificate)
#
# 3. Recover a deleted certificate (begin_recover_deleted_certificate)
#
# 4. Purge a deleted certificate (purge_deleted_certificate)
# ----------------------------------------------------------------------------------------------------------


# Instantiate a backup client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_url=VAULT_URL, credential=credential)

# Let's create certificates holding storage and bank accounts credentials. If the certificate
# already exists in the Key Vault, then a new version of the certificate is created.
print("\n.. Create Certificates")

bank_cert_name = "BankRecoverCertificate"
storage_cert_name = "ServerRecoverCertificate"

bank_certificate_poller = client.begin_create_certificate(
    certificate_name=bank_cert_name, policy=CertificatePolicy.get_default()
)
storage_certificate_poller = client.begin_create_certificate(
    certificate_name=storage_cert_name, policy=CertificatePolicy.get_default()
)

bank_certificate = bank_certificate_poller.result()
storage_certificate = storage_certificate_poller.result()
print("Certificate with name '{0}' was created.".format(bank_certificate.name))
print("Certificate with name '{0}' was created.".format(storage_certificate.name))

# The storage account was closed, need to delete its credentials from the Key Vault.
print("\n.. Delete a Certificate")
deleted_bank_poller = client.begin_delete_certificate(bank_cert_name)
deleted_bank_certificate = deleted_bank_poller.result()
# To ensure certificate is deleted on the server side.
deleted_bank_poller.wait()

print(
    "Certificate with name '{0}' was deleted on date {1}.".format(
        deleted_bank_certificate.name, deleted_bank_certificate.deleted_on
    )
)

# We accidentally deleted the bank account certificate. Let's recover it.
# A deleted certificate can only be recovered if the Key Vault is soft-delete enabled.
print("\n.. Recover Deleted Certificate")
recovered_bank_poller = client.begin_recover_deleted_certificate(deleted_bank_certificate.name)
recovered_bank_certificate = recovered_bank_poller.result()
# To ensure certificate is recovered on the server side.
recovered_bank_poller.wait()
print("Recovered Certificate with name '{0}'.".format(recovered_bank_certificate.name))

# Let's delete the storage certificate now.
# If the keyvault is soft-delete enabled, then for permanent deletion deleted certificate needs to be purged.
client.begin_delete_certificate(storage_cert_name).wait()

# Certificates will still purge eventually on their scheduled purge date, but calling `purge_deleted_certificate` immediately
# purges.
print("\n.. Purge Deleted Certificate")
client.purge_deleted_certificate(storage_cert_name)
print("Certificate has been permanently deleted.")

print("\nrun_sample done")
