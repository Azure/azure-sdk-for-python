# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificateContact
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates basic CRUD operations for the certificate contacts for a key vault.
#
# 1. Create contacts (set_contacts)
#
# 2. Get contacts (get_contacts)
#
# 3. Delete contacts (delete_contacts)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a certificate client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_url=VAULT_URL, credential=credential)
try:
    # First we create a list of Contacts that we would like to make the certificate contacts for this key vault.
    contact_list = [
        CertificateContact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
        CertificateContact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
    ]

    # Creates and sets the certificate contacts for this key vault.
    client.set_contacts(contact_list)

    # Gets the certificate contacts for this key vault.
    contacts = client.get_contacts()
    for contact in contacts:
        print(contact.name)
        print(contact.email)
        print(contact.phone)

    # Deletes all of the certificate contacts for this key vault.
    client.delete_contacts()

except HttpResponseError as e:
    print("\nrun_sample has caught an error. {0}".format(e.message))

finally:
    print("\nrun_sample done")
