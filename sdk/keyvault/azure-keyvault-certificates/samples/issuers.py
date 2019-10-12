# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import AdministratorDetails, CertificateClient
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

# Instantiate a certificate client that will be used to call the service.
# Notice that the client is using default Azure credentials.
# To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
# 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
VAULT_ENDPOINT = os.environ["VAULT_ENDPOINT"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_endpoint=VAULT_ENDPOINT, credential=credential)
try:
    # First we specify the AdministratorDetails for our issuers.
    admin_details = [
        AdministratorDetails(first_name="John", last_name="Doe", email="admin@microsoft.com", phone="4255555555")
    ]

    # Next we create an issuer with these administrator details
    # The name field refers to the name you would like to get the issuer. There are also pre-set names, such as 'Self' and 'Unknown'
    # The provider for your issuer must exist for your vault location and tenant id.
    client.create_issuer(
        name="issuer1", provider="Test", account_id="keyvaultuser", admin_details=admin_details, enabled=True
    )

    # Now we get this issuer by name
    issuer1 = client.get_issuer(name="issuer1")

    print(issuer1.name)
    print(issuer1.properties.provider)
    print(issuer1.account_id)

    for admin_detail in issuer1.admin_details:
        print(admin_detail.first_name)
        print(admin_detail.last_name)
        print(admin_detail.email)
        print(admin_detail.phone)

    # Now we will list all of the certificate issuers for this key vault. To better demonstrate this, we will first create another issuer.
    client.create_issuer(name="issuer2", provider="Test", account_id="keyvaultuser", enabled=True)

    issuers = client.list_issuers()

    for issuer in issuers:
        print(issuer.name)
        print(issuer.provider)

    # Finally, we delete our first issuer by name.
    client.delete_issuer(name="issuer1")

except HttpResponseError as e:
    print("\nrun_sample has caught an error. {0}".format(e.message))

finally:
    print("\nrun_sample done")
