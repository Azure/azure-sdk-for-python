# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic list operations on a vault(certificate) resource for Azure Key Vault.
# The vault has to be soft-delete enabled to perform one of the following operations: https://docs.microsoft.com/azure/key-vault/key-vault-ovw-soft-delete
#
# 1. Create certificate (begin_create_certificate)
#
# 2. List certificates from the Key Vault (list_properties_of_certificates)
#
# 3. List certificate versions from the Key Vault (list_properties_of_certificate_versions)
#
# 4. List deleted certificates from the Key Vault (list_deleted_certificates). The vault has to be soft-delete enabled
# to perform this operation.
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a certificate client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_url=VAULT_URL, credential=credential)

# Let's create a certificate for holding storage and bank accounts credentials. If the certificate
# already exists in the Key Vault, then a new version of the certificate is created.
print("\n.. Create Certificate")
bank_cert_name = "BankListCertificate"
storage_cert_name = "StorageListCertificate"

bank_certificate_poller = client.begin_create_certificate(
    certificate_name=bank_cert_name, policy=CertificatePolicy.get_default()
)
storage_certificate_poller = client.begin_create_certificate(
    certificate_name=storage_cert_name, policy=CertificatePolicy.get_default()
)

# await the creation of the bank and storage certificate
bank_certificate = bank_certificate_poller.result()
storage_certificate = storage_certificate_poller.result()

print(f"Certificate with name '{bank_certificate.name}' was created.")
print(f"Certificate with name '{storage_certificate.name}' was created.")

# Let's list the certificates.
print("\n.. List certificates from the Key Vault")
certificates = client.list_properties_of_certificates()
for certificate in certificates:
    print(f"Certificate with name '{certificate.name}' was found.")

# You've decided to add tags to the certificate you created. Calling begin_create_certificate on an existing
# certificate creates a new version of the certificate in the Key Vault with the new value.

tags = {"a": "b"}
bank_certificate_poller = client.begin_create_certificate(
    certificate_name=bank_cert_name, policy=CertificatePolicy.get_default(), tags=tags
)
bank_certificate = bank_certificate_poller.result()
print(
    f"Certificate with name '{bank_certificate.name}' was created again with tags '{bank_certificate.properties.tags}'"
)

# You need to check all the different tags your bank account certificate had previously. Let's print
# all the versions of this certificate.
print("\n.. List versions of the certificate using its name")
certificate_versions = client.list_properties_of_certificate_versions(bank_cert_name)
for certificate_version in certificate_versions:
    print(
        f"Bank Certificate with name '{certificate_version.name}' with version '{certificate_version.version}' "
        f"has tags: '{certificate_version.tags}'."
    )

# The bank account and storage accounts got closed. Let's delete bank and storage accounts certificates.
# We call wait() to ensure the certificate is deleted server side because the following method requires
# server-side deletion to run properly. In most situations you will not have to call wait().
client.begin_delete_certificate(bank_cert_name).wait()
client.begin_delete_certificate(storage_cert_name).wait()

# You can list all the deleted and non-purged certificates, assuming Key Vault is soft-delete enabled.
print("\n.. List deleted certificates from the Key Vault")
deleted_certificates = client.list_deleted_certificates()
for deleted_certificate in deleted_certificates:
    print(f"Certificate with name '{deleted_certificate.name}' has recovery id '{deleted_certificate.recovery_id}'")

print("\nrun_sample done")
