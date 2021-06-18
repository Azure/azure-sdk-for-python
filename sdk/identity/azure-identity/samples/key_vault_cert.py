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
from azure.keyvault.certificates import (
    CertificateClient,
    CertificateContentType,
    CertificatePolicy,
    WellKnownIssuerNames,
)
from azure.keyvault.secrets import SecretClient

VAULT_URL = os.environ["VAULT_URL"]

credential = DefaultAzureCredential()

# a CertificateClient to create self-signed certs to work with
CERT_CLIENT = CertificateClient(VAULT_URL, credential)

# Key Vault stores certificate private keys as secrets, so we use a SecretClient to retrieve them
SECRET_CLIENT = SecretClient(VAULT_URL, credential)


def pkcs12_cert():
    """Demonstrates creating a CertificateCredential with a Key Vault certificate stored in PKCS12 (default) format"""

    # Creating a self-signed cert to work with
    create_cert_poller = CERT_CLIENT.begin_create_certificate(
        "azure-identity-sample-default", CertificatePolicy.get_default()
    )
    cert = create_cert_poller.result()

    # CertificateCredential requires the certificate and its private key in PEM format.
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

    # cryptography can convert PKCS12 to PEM
    def pkcs12_to_pem(pkcs12_bytes):
        """Convert certificate bytes from PKCS12 format to PEM using the "cryptography" library"""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.serialization import Encoding, pkcs12, PrivateFormat, NoEncryption

        private_key, cert, additional_certs = pkcs12.load_key_and_certificates(
            pkcs12_bytes, password=None, backend=default_backend()
        )

        # using NoEncryption because the certificate created above is not password protected
        private_bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        pem_sections = [private_bytes] + [c.public_bytes(Encoding.PEM) for c in [cert] + additional_certs]
        return b"".join(pem_sections)

    pem_bytes = pkcs12_to_pem(pkcs12_bytes)

    # This credential will load the certificate but can't actually authenticate. Authentication requires real
    # tenant and client IDs for a service principal configured to accept the certificate.
    CertificateCredential("tenant-id", "client-id", certificate_data=pem_bytes)


def pem_cert():
    """Demonstrates creating a CertificateCredential with a Key Vault certificate stored in PEM format"""

    # creating a self-signed certificate stored in PEM format (PKCS12 is Key Vault's default format)
    pem_policy = CertificatePolicy(
        WellKnownIssuerNames.self, subject="CN=localhost", content_type=CertificateContentType.pem
    )
    pem_cert = CERT_CLIENT.begin_create_certificate("azure-identity-sample-pem", pem_policy).result()

    # verifying the certificate is exportable and stored in PEM format, to
    # demonstrate how you would do so when you don't already have its policy
    policy = CERT_CLIENT.get_certificate_policy(pem_cert.name)
    assert policy.exportable, "Expected an exportable certificate because that's Key Vault's default"
    assert policy.content_type == CertificateContentType.pem

    # Because the certificate is exportable, it's available (with its private key) as a secret
    pem_cert_secret = SECRET_CLIENT.get_secret(pem_cert.name)

    # The secret's value is a string; CertificateCredential requires bytes
    pem_bytes = pem_cert_secret.value.encode()

    # This credential will load the certificate but can't actually authenticate. Authentication requires real
    # tenant and client IDs for a service principal configured to accept the certificate.
    CertificateCredential("tenant-id", "client-id", certificate_data=pem_bytes)


if __name__ == "__main__":
    pkcs12_cert()
    pem_cert()
