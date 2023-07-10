# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy, CertificateContentType, WellKnownIssuerNames

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
# Sample - demonstrates the basic CRUD operations on a vault(certificate) resource for Azure Key Vault
#
# 1. Create a new certificate (begin_create_certificate)
#
# 2. Get an existing certificate (get_certificate)
#
# 3. Update an existing certificate (update_certificate)
#
# 4. Delete a certificate (begin_delete_certificate)
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a certificate client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_a_certificate_client]
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = CertificateClient(vault_url=VAULT_URL, credential=credential)
# [END create_a_certificate_client]

# Let's create a certificate for holding account credentials valid for 1 year.
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

# begin_create_certificate returns a poller. Calling result() on the poller will return the certificate
# as a KeyVaultCertificate if creation is successful, and the CertificateOperation if not. The wait()
# call on the poller will wait until the long running operation is complete.
# [START create_a_certificate]
new_certificate = client.begin_create_certificate(
    certificate_name=cert_name, policy=cert_policy
).result()
# [END create_a_certificate]
print(f"Certificate with name '{new_certificate.name}' created")


# Let's get the certificate using its name
print("\n.. Get a certificate by name")
# [START get_certificate]
certificate = client.get_certificate(cert_name)
# [END get_certificate]
print(f"Certificate with name '{certificate.name}' was found'.")

# After one year, the account is still active, and we have decided to update the tags.
print("\n.. Update a certificate by name")
# [START update_certificate]
tags = {"a": "b"}
updated_certificate = client.update_certificate_properties(
    certificate_name=certificate.name, tags=tags
)
# [END update_certificate]
print(
    f"Certificate with name '{certificate.name}' was updated on date '{updated_certificate.properties.updated_on}'"
)
print(
    f"Certificate with name '{certificate.name}' was updated with tags '{updated_certificate.properties.tags}'"
)

# The account was closed, need to delete its credentials from the Key Vault.
print("\n.. Delete certificate")
# [START delete_certificate]
deleted_certificate = client.begin_delete_certificate(certificate.name).result()
# [END delete_certificate]
print(f"Certificate with name '{deleted_certificate.name}' was deleted.")

print("\nrun_sample done")
