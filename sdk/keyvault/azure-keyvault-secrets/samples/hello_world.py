# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import datetime
import os

from azure.keyvault.secrets import SecretClient, ContentType
from azure.keyvault.certificates import (
    CertificateClient,
    CertificatePolicy,
    CertificateContentType,
    WellKnownIssuerNames,
)
from azure.identity import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://learn.microsoft.com/azure/key-vault/quick-create-cli)
#
#  2. Microsoft Azure Key Vault PyPI package -
#    https://pypi.python.org/pypi/azure-keyvault-secrets/
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a vault(secret) resource for Azure Key Vault
#
# 1. Create a new Secret (set_secret)
#
# 2. Get an existing secret (get_secret)
#
# 3. Update an existing secret (set_secret)
#
# 4. Delete a secret (begin_delete_secret)
#
# 5. Get a certificate-backed secret with out_content_type (get_secret with out_content_type)
#
# 6. Check previous_version on a secret with multiple versions
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a secret client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_secret_client]
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)
# [END create_secret_client]

# Let's create a secret holding bank account credentials valid for 1 year.
# if the secret already exists in the Key Vault, then a new version of the secret is created.
print("\n.. Create Secret")
expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
secret = client.set_secret("helloWorldSecretName", "helloWorldSecretValue", expires_on=expires)
assert secret.name
print(f"Secret with name '{secret.name}' created with value '{secret.value}'")
print(f"Secret with name '{secret.name}' expires on '{secret.properties.expires_on}'")

# Let's get the bank secret using its name
print("\n.. Get a Secret by name")
bank_secret = client.get_secret(secret.name)
assert bank_secret.properties.expires_on
print(f"Secret with name '{bank_secret.name}' was found with value '{bank_secret.value}'.")

# After one year, the bank account is still active, we need to update the expiry time of the secret.
# The update method can be used to update the expiry attribute of the secret. It cannot be used to update
# the value of the secret.
print("\n.. Update a Secret by name")
expires = bank_secret.properties.expires_on + datetime.timedelta(days=365)
updated_secret_properties = client.update_secret_properties(secret.name, expires_on=expires)
print(f"Secret with name '{secret.name}' was updated on date '{updated_secret_properties.updated_on}'")
print(f"Secret with name '{secret.name}' was updated to expire on '{updated_secret_properties.expires_on}'")

# Bank forced a password update for security purposes. Let's change the value of the secret in the Key Vault.
# To achieve this, we need to create a new version of the secret in the Key Vault. The update operation cannot
# change the value of the secret.
new_secret = client.set_secret(secret.name, "newSecretValue")
print(f"Secret with name '{new_secret.name}' created with value '{new_secret.value}'")

# When a new version of a secret is created, the service may return `previous_version` to track
# version history. This is especially useful for certificate-backed secrets.
print(f"Secret's previous version: {new_secret.properties.previous_version}")

# The bank account was closed, need to delete its credentials from the Key Vault.
print("\n.. Deleting Secret...")
client.begin_delete_secret(secret.name)
print(f"Secret with name '{secret.name}' was deleted.")

# --------------------------------------------------------------------------------------------------------
# Demonstrate out_content_type: retrieve a certificate-backed secret in a different encoding format.
# When a certificate is stored in PFX (PKCS#12) format, you can retrieve its secret value as PEM.
# --------------------------------------------------------------------------------------------------------
print("\n.. Create a PFX certificate to demonstrate out_content_type")
cert_client = CertificateClient(vault_url=VAULT_URL, credential=credential)
cert_name = "outContentTypeSampleCert"
cert_policy = CertificatePolicy(
    issuer_name=WellKnownIssuerNames.self,
    subject="CN=outContentTypeDemo",
    content_type=CertificateContentType.pkcs12,
)
cert = cert_client.begin_create_certificate(certificate_name=cert_name, policy=cert_policy).result()
print(f"Certificate '{cert.name}' created (PFX format)")

# Get the certificate-backed secret in its default format (PFX/base64)
# [START get_secret_with_out_content_type]
pfx_secret = client.get_secret(cert_name)
print(f"Default secret content type: {pfx_secret.properties.content_type}")

# Now retrieve the same secret as PEM using out_content_type
pem_secret = client.get_secret(cert_name, out_content_type=ContentType.PEM)
print(f"PEM secret content type: {pem_secret.properties.content_type}")
assert pem_secret.value and "-----BEGIN" in pem_secret.value
print("Successfully retrieved certificate secret in PEM format")
# [END get_secret_with_out_content_type]

# Clean up the certificate
print("\n.. Deleting certificate...")
cert_client.begin_delete_certificate(cert_name).result()
print(f"Certificate '{cert_name}' was deleted.")

print("\nrun_sample done")
