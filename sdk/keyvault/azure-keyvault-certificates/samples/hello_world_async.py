# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates import CertificatePolicy, CertificateContentType, WellKnownIssuerNames
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, VAULT_URL. (See
#    https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a vault(certificate) resource for Azure Key Vault
#
# 1. Create a new certificate (create_certificate)
#
# 2. Get an existing certificate (get_certificate)
#
# 3. Update an existing certificate (update_certificate)
#
# 4. Delete a certificate (delete_certificate)
#
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
        # Let's create a certificate for holding bank account credentials valid for 1 year.
        # if the certificate already exists in the Key Vault, then a new version of the certificate is created.
        print("\n.. Create certificate")

        # Before creating your certificate, let's create the management policy for your certificate.
        # Here you specify the properties of the key, secret, and issuer backing your certificate,
        # the X509 component of your certificate, and any lifetime actions you would like to be taken
        # on your certificate

        # Alternatively, if you would like to use our default policy, use CertificatePolicy.get_default()
        cert_policy = CertificatePolicy(
            issuer_name=WellKnownIssuerNames.self,
            subject="CN=*.microsoft.com",
            san_dns_names=["sdk.azure-int.net"],
            exportable=True,
            key_type="RSA",
            key_size=2048,
            reuse_key=False,
            content_type=CertificateContentType.pkcs12,
            validity_in_months=24,
        )
        cert_name = "HelloWorldCertificate"

        # Awaiting create_certificate will return the certificate as a KeyVaultCertificate
        # if creation is successful, and the CertificateOperation if not.
        certificate = await client.create_certificate(certificate_name=cert_name, policy=cert_policy)
        print("Certificate with name '{0}' created".format(certificate.name))

        # Let's get the bank certificate using its name
        print("\n.. Get a certificate by name")
        bank_certificate = await client.get_certificate(cert_name)
        print("Certificate with name '{0}' was found.".format(bank_certificate.name))

        # After one year, the bank account is still active, and we have decided to update the tags.
        print("\n.. Update a certificate by name")
        tags = {"a": "b"}
        updated_certificate = await client.update_certificate_properties(
            certificate_name=bank_certificate.name, tags=tags
        )
        print(
            "Certificate with name '{0}' was updated on date '{1}'".format(
                bank_certificate.name, updated_certificate.properties.updated_on
            )
        )
        print(
            "Certificate with name '{0}' was updated with tags '{1}'".format(
                bank_certificate.name, updated_certificate.properties.tags
            )
        )

        # The bank account was closed, need to delete its credentials from the Key Vault.
        print("\n.. Delete certificate")
        deleted_certificate = await client.delete_certificate(bank_certificate.name)
        print("Deleting certificate..")
        print("Certificate with name '{0}' was deleted.".format(deleted_certificate.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")
        await credential.close()
        await client.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level error: {0}".format(str(e)))
