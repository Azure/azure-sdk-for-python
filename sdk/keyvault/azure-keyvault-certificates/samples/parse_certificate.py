# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.keyvault.secrets import SecretClient
from cryptography.hazmat.primitives.serialization import pkcs12

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault. (https://docs.microsoft.com/azure/key-vault/quick-create-cli)
#
# 2. A service principal with certificate get, delete, and purge permissions, as well as secret get
#    permissions.
#
# 3. azure-keyvault-certificates, azure-keyvault-secrets, azure-identity, and cryptography (v3.3+) packages
#    (pip install these).
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to get the private key of an existing Key Vault certificate
#
# 1. Create a new certificate (CertificateClient.begin_create_certificate)
#
# 2. Get a certificate secret (SecretClient.get_secret)
#
# 3. Delete a certificate (CertificateClient.begin_delete_certificate)
#
# 4. Purge a certificate (CertificateClient.purge_deleted_secret)
#
# ----------------------------------------------------------------------------------------------------------

# Instantiate a certificate client that will be used to call the service.
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
cert_name = "PrivateKeyCertificate"
cert_policy = CertificatePolicy.get_default()

# begin_create_certificate returns a poller. Calling result() on the poller will return the certificate
# as a KeyVaultCertificate if creation is successful, and the CertificateOperation if not. The wait()
# call on the poller will wait until the long running operation is complete.
created_certificate = certificate_client.begin_create_certificate(
    certificate_name=cert_name, policy=cert_policy
).result()
print(f"Certificate with name '{created_certificate.name}' was created")

# Key Vault also creates a secret with the same name as the created certificate.
# This secret contains the certificate's bytes, which include the private key if the certificate's
# policy indicates that the key is exportable.
print("\n.. Get a secret by name")
certificate_secret = secret_client.get_secret(name=cert_name)
print(f"Certificate secret with name '{certificate_secret.name}' was found.")

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
print(f"Certificate with name '{certificate_secret.name}' was parsed.")

# Now we can clean up the vault by deleting, then purging, the certificate.
print("\n.. Delete certificate")
delete_operation_poller = certificate_client.begin_delete_certificate(
    certificate_name=cert_name
)
deleted_certificate = delete_operation_poller.result()
delete_operation_poller.wait()
print(f"Certificate with name '{deleted_certificate.name}' was deleted.")

certificate_client.purge_deleted_certificate(certificate_name=deleted_certificate.name)
print(f"Certificate with name '{deleted_certificate.name}' is being purged.")

print("\nrun_sample done")
