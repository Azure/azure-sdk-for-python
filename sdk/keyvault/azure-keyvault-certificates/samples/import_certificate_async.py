# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates import CertificateContentType, CertificatePolicy, WellKnownIssuerNames
from azure.keyvault.certificates.aio import CertificateClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates#authenticate-the-client)
#
# 4. A PFX certificate on your machine. Set an environment variable, PFX_CERT_PATH, with the path to this certificate.
#
# 5. A PEM-formatted certificate on your machine. Set an environment variable, PEM_CERT_PATH, with the path to this
#    certificate.
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates importing a PFX and PEM-formatted certificate into Azure Key Vault
#
# 1. Import an existing PFX certificate (import_certificate)
#
# 2. Import an existing PEM-formatted certificate (import_certificate)
#
# ----------------------------------------------------------------------------------------------------------

async def run_sample():
    # Instantiate a backup client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    VAULT_URL = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=VAULT_URL, credential=credential)

    # Let's import a PFX certificate first.
    # Assuming you already have a PFX containing your key pair, you can import it into Key Vault.
    # You can do this without setting a policy, but the policy is needed if you want the private key to be exportable
    # or to configure actions when a certificate is close to expiration.
    pfx_cert_name = "pfxCertAsync"
    with open(os.environ["PFX_CERT_PATH"], "rb") as f:
        pfx_cert_bytes = f.read()
    imported_pfx_cert = await client.import_certificate(
        certificate_name=pfx_cert_name, certificate_bytes=pfx_cert_bytes
    )
    print("PFX certificate '{}' imported successfully.".format(imported_pfx_cert.name))

    # Now let's import a PEM-formatted certificate.
    # To import a PEM-formatted certificate, you must provide a CertificatePolicy that sets the content_type to
    # CertificateContentType.pem or the certificate will fail to import (the default content type is PFX).
    pem_cert_name = "pemCertAsync"
    with open(os.environ["PEM_CERT_PATH"], "rb") as f:
        pem_cert_bytes = f.read()
    pem_cert_policy = CertificatePolicy(issuer_name=WellKnownIssuerNames.self, content_type=CertificateContentType.pem)
    imported_pem_cert = await client.import_certificate(
        certificate_name=pem_cert_name, certificate_bytes=pem_cert_bytes, policy=pem_cert_policy
    )
    print("PEM-formatted certificate '{}' imported successfully.".format(imported_pem_cert.name))

    await credential.close()
    await client.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
