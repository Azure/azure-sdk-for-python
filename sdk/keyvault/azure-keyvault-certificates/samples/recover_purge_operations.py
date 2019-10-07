# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import time
from azure.keyvault.certificates import CertificateClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_ENDPOINT
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic recover and purge operations on a vault(certificate) resource for Azure Key Vault
#
# 1. Create a certificate (create_certificate)
#
# 2. Delete a certificate (delete_certificate)
#
# 3. Recover a deleted certificate (recover_deleted_certificate)
#
# 4. Purge a deleted certificate (purge_deleted_certificate)
# ----------------------------------------------------------------------------------------------------------


# Instantiate a certificate client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_ENDPOINT = os.environ["VAULT_ENDPOINT"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_endpoint=VAULT_ENDPOINT, credential=credential)
try:
    # Let's create certificates holding storage and bank accounts credentials. If the certificate
    # already exists in the Key Vault, then a new version of the certificate is created.
    print("\n.. Create Certificates")

    bank_cert_name = "BankRecoverCertificate"
    storage_cert_name = "ServerRecoverCertificate"

    bank_certificate_poller = client.create_certificate(name=bank_cert_name)
    storage_certificate_poller = client.create_certificate(name=storage_cert_name)

    bank_certificate = bank_certificate_poller.result()
    storage_certificate = storage_certificate_poller.result()
    print("Certificate with name '{0}' was created.".format(bank_certificate.name))
    print("Certificate with name '{0}' was created.".format(storage_certificate.name))

    # The storage account was closed, need to delete its credentials from the Key Vault.
    print("\n.. Delete a Certificate")
    deleted_bank_certificate = client.delete_certificate(name=bank_cert_name)
    # To ensure certificate is deleted on the server side.
    time.sleep(30)

    print(
        "Certificate with name '{0}' was deleted on date {1}.".format(
            deleted_bank_certificate.name, deleted_bank_certificate.deleted_date
        )
    )

    # We accidentally deleted the bank account certificate. Let's recover it.
    # A deleted certificate can only be recovered if the Key Vault is soft-delete enabled.
    print("\n.. Recover Deleted Certificate")
    recovered_bank_certificate = client.recover_deleted_certificate(deleted_bank_certificate.name)
    print("Recovered Certificate with name '{0}'.".format(recovered_bank_certificate.name))

    # Let's delete the storage certificate now.
    # If the keyvault is soft-delete enabled, then for permanent deletion deleted certificate needs to be purged.
    client.delete_certificate(name=storage_cert_name)
    # To ensure certificate is deleted on the server side.
    time.sleep(30)

    # To ensure permanent deletion, we might need to purge the secret.
    print("\n.. Purge Deleted Certificate")
    client.purge_deleted_certificate(name=storage_cert_name)
    print("Certificate has been permanently deleted.")

except HttpResponseError as e:
    if "(NotSupported)" in e.message:
        print("\n{0} Please enable soft delete on Key Vault to perform this operation.".format(e.message))
    else:
        print("\nrun_sample has caught an error. {0}".format(e.message))

finally:
    print("\nrun_sample done")
