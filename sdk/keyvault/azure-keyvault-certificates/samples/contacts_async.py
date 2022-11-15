# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates import CertificateContact

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
# Sample - demonstrates basic CRUD operations for the certificate contacts for a key vault.
#
# 1. Create contacts (set_contacts)
#
# 2. Get contacts (get_contacts)
#
# 3. Delete contacts (delete_contacts)
# ----------------------------------------------------------------------------------------------------------


async def run_sample():
    # Instantiate a certificate client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=VAULT_URL, credential=credential)

    contact_list = [
        CertificateContact(email="admin@contoso.com", name="John Doe", phone="1111111111"),
        CertificateContact(email="admin2@contoso.com", name="John Doe2", phone="2222222222"),
    ]

    # Creates and sets the certificate contacts for this key vault.
    await client.set_contacts(contact_list)

    # Gets the certificate contacts for this key vault.
    contacts = await client.get_contacts()
    for contact in contacts:
        print(contact.name)
        print(contact.email)
        print(contact.phone)

    # Deletes all of the certificate contacts for this key vault.
    await client.delete_contacts()

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
