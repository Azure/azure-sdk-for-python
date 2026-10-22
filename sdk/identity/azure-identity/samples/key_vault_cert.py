# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Demonstrates how to authenticate with a certificate stored in Azure Key Vault

To run this script, first set $VAULT_URL and ensure DefaultAzureCredential is able
to authenticate you. The script creates a couple of self-signed certs in the given
Vault, retrieves their private keys, and constructs an instance of CertificateCredential
with each.
"""
import base64
import os

from azure.identity import CertificateCredential, DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificateContentType, CertificatePolicy
from azure.keyvault.secrets import SecretClient

VAULT_URL = os.environ["VAULT_URL"]

credential = DefaultAzureCredential()

# a CertificateClient to create self-signed certs to work with
CERT_CLIENT = CertificateClient(VAULT_URL, credential)

# Key Vault stores certificate private keys as secrets, so we use a SecretClient to retrieve them
SECRET_CLIENT = SecretClient(VAULT_URL, credential)

# Creating a self-signed cert to work with
create_cert_poller = CERT_CLIENT.begin_create_certificate("azure-identity-sample", CertificatePolicy.get_default())
cert = create_cert_poller.result()

# The certificate as returned by begin_create_certificate() or get_certificate() contains
# only the public portion of the certificate. Key Vault will release the private key only
# if the certificate's policy indicates it's exportable (certs are exportable by default).
policy = CERT_CLIENT.get_certificate_policy(cert.name)
assert policy.exportable, "Expected an exportable certificate because that's Key Vault's default"

# The policy's content_type indicates whether the certificate is stored in PEM or PKCS12 format
assert policy.content_type == CertificateContentType.pkcs12, "Expected PKCS12 because that's Key Vault's default"

# Key Vault stores the complete certificate, with its private key, as a secret sharing the certificate's name
# Because this certificate is stored in PKCS12 format, the secret's value is base64 encoded bytes
encoded_cert = SECRET_CLIENT.get_secret(cert.name).value
pkcs12_bytes = base64.b64decode(encoded_cert)

# This credential will load the certificate but can't actually authenticate. Authentication requires real
# tenant and client IDs for a service principal configured to accept the certificate.
CertificateCredential("tenant-id", "client-id", certificate_data=pkcs12_bytes)
