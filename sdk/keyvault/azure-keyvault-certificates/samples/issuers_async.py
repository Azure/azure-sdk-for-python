# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import AdministratorDetails, CertificateClient
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Key Vault-
#    https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-certificates/
#
# 3. Microsoft Azure Identity package -
#    https://pypi.python.org/pypi/azure-identity/
#
# 4. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL.
# How to do this - https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates#createget-credentials)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates basic CRUD operations for certificate issuers.
#
# 1. Create an issuer (create_issuer)
#
# 2. Get an issuer (get_issuer)
#
# 3. List issuers for the key vault (list_issuers)
#
# 4. Update an issuer (update_issuer)
#
# 5. Delete an issuer (delete_issuer)
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a certificate client that will be used to call the service.
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=VAULT_URL, credential=credential)
    try:
        # First we specify the AdministratorDetails for our issuers.
        admin_details = [AdministratorDetails(
            first_name="John",
            last_name="Doe",
            email="admin@microsoft.com",
            phone="4255555555"
        )]

        # Next we create an issuer with these administrator details
        # The name field refers to the name you would like to get the issuer. There are also pre-set names, such as 'Self' and 'Unknown'
        await client.create_issuer(
            name="issuer1",
            provider="Sample",
            account_id="keyvaultuser",
            admin_details=admin_details,
            enabled=True
        )

        # Now we get this issuer by name
        issuer1 = await client.get_issuer(name="issuer1")

        print(issuer1.name)
        print(issuer1.provider)
        print(issuer1.account_id)
        print(issuer1.admin_details.first_name)
        print(issuer1.admin_details.last_name)
        print(issuer1.admin_details.email)
        print(issuer1.admin_details.phone)

        # Now we will list all of the certificate issuers for this key vault. To better demonstrate this, we will first create another issuer.
        await client.create_issuer(
            name="issuer2",
            provider="Sample",
            account_id="keyvaultuser",
            enabled=True
        )

        issuers = client.list_issuers()

        async for issuer in issuers:
            print(issuer.name)
            print(issuer.provider)

        # Finally, we delete our first issuer by name.
        await client.delete_issuer(name="issuer1")

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))