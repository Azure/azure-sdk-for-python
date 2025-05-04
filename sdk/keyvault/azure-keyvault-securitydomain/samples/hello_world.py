# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from json import loads
import os

from azure.keyvault.securitydomain.models import CertificateInfo, SecurityDomainJsonWebKey

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault Managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. Three JSON files, containing JWKs, to be used as security domain wrapping keys. Set environment variables
#    SD_KEY_1, SD_KEY_2, and SD_KEY_3 to the paths of the files.
#
# 3. azure-keyvault-securitydomain and azure-identity libraries (pip install these)
#
# 4. Set environment variable VAULT_URL with the URL of your managed HSM
#
# 5. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the security domain download operations for Azure Key Vault Managed HSM
#
# 1. Download a security domain (begin_download)
# ----------------------------------------------------------------------------------------------------------

# Instantiate a security domain client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_a_security_domain_client]
from azure.identity import DefaultAzureCredential
from azure.keyvault.securitydomain import SecurityDomainClient

VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecurityDomainClient(vault_url=VAULT_URL, credential=credential)
# [END create_a_security_domain_client]

# Load the JWKs into SecurityDomainJsonWebKey objects, to provide to a CertificateInfo object.
print("Preparing security domain wrapping keys.")
sd_wrapping_keys = [os.environ["SD_KEY_1"], os.environ["SD_KEY_2"], os.environ["SD_KEY_3"]]
certificates = []
for path in sd_wrapping_keys:
    with open(path, "rb") as f:
        jwk = loads(f.read())
    certificates.append(SecurityDomainJsonWebKey(jwk))
certs_object = CertificateInfo(certificates=certificates)

# Download the security domain. Without passing `skip_activation_polling=True`, calling `.result()` on the returned
# poller will wait for HSM activation to complete. By passing the argument, the poller will return immediately with
# the security domain instead (activation status can be checked with `client.get_download_status`).
print("Beginning security domain download.")
poller = client.begin_download(certificate_info=certs_object, skip_activation_polling=True)
security_domain = poller.result()
print("Security domain downloaded successfully.")
