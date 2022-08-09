# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import base64
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates import CertificatePolicy
from azure.keyvault.secrets.aio import SecretClient
from cryptography.hazmat.primitives.serialization import pkcs12

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault. (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. A service principal with certificate get, delete, and purge permissions, as well as secret get
#    permissions.
#
# 3. azure-keyvault-certificates, azure-keyvault-secrets, azure-identity, and cryptography (v3.3+) packages
#    (pip install these).
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to get the private key of an existing Key Vault certificate
#
# 1. Create a new certificate (CertificateClient.create_certificate)
#
# 2. Get a certificate secret (SecretClient.get_secret)
#
# 3. Delete a certificate (CertificateClient.delete_certificate)
#
# 4. Purge a certificate (CertificateClient.purge_deleted_secret)
#
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a backup client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    certificate_client = CertificateClient(vault_url=VAULT_URL, credential=credential)

    # Instantiate a secret client that will be used to call the service.
    # Notice that this client can reuse the credential object created above.
    secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)

    # Let's create a certificate in the vault.
    # If the certificate already exists in the Key Vault, then a new version of the certificate is created.
    print("\n.. Create certificate")

    # Before creating your certificate, let's create the management policy for your certificate.
    # Here we use the default policy.
    cert_name = "PrivateKeyCertificateAsync"
    cert_policy = CertificatePolicy.get_default()

    # Awaiting create_certificate will return the certificate as a KeyVaultCertificate
    # if creation is successful, and the CertificateOperation if not.
    created_certificate = await certificate_client.create_certificate(
        certificate_name=cert_name, policy=cert_policy
    )
    print("Certificate with name '{}' was created".format(created_certificate.name))

    # Key Vault also creates a secret with the same name as the created certificate.
    # This secret contains protected information about the certificate, such as its private key.
    print("\n.. Get a secret by name")
    certificate_secret = await secret_client.get_secret(name=cert_name)
    print("Certificate secret with name '{}' was found.".format(certificate_secret.name))

    # Now we can extract the private key and public certificate from the secret using the cryptography
    # package. `additional_certificates` will be empty since the secret only contains one certificate.
    # This example shows how to parse a certificate in PKCS12 format since it's the default in Key Vault,
    # but PEM certificates are supported as well. With a PEM certificate, you could use load_pem_private_key
    # in place of load_key_and_certificates.
    cert_bytes = base64.b64decode(certificate_secret.value)
    private_key, public_certificate, additional_certificates = pkcs12.load_key_and_certificates(
        data=cert_bytes,
        password=None
    )
    print("Certificate with name '{}' was parsed.".format(certificate_secret.name))

    # Now we can clean up the vault by deleting, then purging, the certificate.
    print("\n.. Delete certificate")
    deleted_certificate = await certificate_client.delete_certificate(certificate_name=cert_name)
    print("Certificate with name '{}' was deleted.".format(deleted_certificate.name))

    await certificate_client.purge_deleted_certificate(certificate_name=deleted_certificate.name)
    print("Certificate with name '{}' is being purged.".format(deleted_certificate.name))

    print("\nrun_sample done")
    await credential.close()
    await certificate_client.close()
    await secret_client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
