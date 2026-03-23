# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recorded integration tests for SubjectAlternativeNames — new ip_addresses
and uniform_resource_identifiers fields (API version 2025-07-01).

These tests create real certificates against Azure Key Vault via the test proxy
and validate that new SAN fields are properly round-tripped through the service.
"""

import os
import time

import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, is_live

from azure.keyvault.certificates._generated import KeyVaultClient
from azure.keyvault.certificates._generated.models import (
    CertificateCreateParameters,
    CertificatePolicy,
    IssuerParameters,
    KeyProperties,
    SubjectAlternativeNames,
    X509CertificateProperties,
)


class TestSanLiveOperations(AzureRecordedTestCase):
    """Integration tests that record live traffic for the new SAN fields."""

    def setup_method(self, method):
        # Map KV-specific env vars to standard Azure SDK env vars (matches _test_case.py)
        if is_live():
            os.environ["AZURE_TENANT_ID"] = os.getenv("KEYVAULT_TENANT_ID", "")
            os.environ["AZURE_CLIENT_ID"] = os.getenv("KEYVAULT_CLIENT_ID", "")
            os.environ["AZURE_CLIENT_SECRET"] = os.getenv("KEYVAULT_CLIENT_SECRET", "")

    def _get_vault_url(self):
        return os.environ.get("AZURE_KEYVAULT_URL", "https://vaultname.vault.azure.net")

    def _create_client(self):
        credential = self.get_credential(KeyVaultClient)
        return self.create_client_from_credential(
            KeyVaultClient,
            credential,
            vault_base_url=self._get_vault_url(),
        )

    def _wait_for_operation(self, client, cert_name, timeout=120):
        """Poll until a certificate operation completes or fails."""
        start = time.time()
        while True:
            op = client.get_certificate_operation(cert_name)
            status = (op.status or "").lower()
            if status == "completed":
                return op
            if status in ("failed", "cancelled"):
                raise RuntimeError(f"Certificate operation {status}: {op.error}")
            if time.time() - start > timeout:
                raise TimeoutError(f"Certificate operation timed out after {timeout}s")
            time.sleep(2)

    def _cleanup_cert(self, client, cert_name):
        """Best-effort delete + purge."""
        try:
            client.delete_certificate(cert_name)
            if is_live():
                time.sleep(10)
            client.purge_deleted_certificate(cert_name)
        except Exception:
            pass

    # ---- tests ----

    @recorded_by_proxy
    def test_create_certificate_with_ip_addresses(self):
        """Create a self-signed cert with IP address SANs and verify the policy."""
        client = self._create_client()
        cert_name = self.get_resource_name("livekvtestsanip")

        params = CertificateCreateParameters(
            certificate_policy=CertificatePolicy(
                issuer_parameters=IssuerParameters(name="Self"),
                key_properties=KeyProperties(
                    exportable=True, key_type="RSA", key_size=2048, reuse_key=False,
                ),
                x509_certificate_properties=X509CertificateProperties(
                    subject="CN=TestSanIP",
                    subject_alternative_names=SubjectAlternativeNames(
                        ip_addresses=["10.0.0.1", "192.168.1.100"],
                    ),
                    validity_in_months=12,
                ),
            ),
        )

        try:
            client.create_certificate(cert_name, params)
            self._wait_for_operation(client, cert_name)

            policy = client.get_certificate_policy(cert_name)
            san = policy.x509_certificate_properties.subject_alternative_names
            assert san is not None
            assert san.ip_addresses is not None
            assert set(san.ip_addresses) == {"10.0.0.1", "192.168.1.100"}
        finally:
            self._cleanup_cert(client, cert_name)

    @recorded_by_proxy
    def test_create_certificate_with_uris(self):
        """Create a self-signed cert with URI SANs and verify the policy."""
        client = self._create_client()
        cert_name = self.get_resource_name("livekvtestsanuri")

        params = CertificateCreateParameters(
            certificate_policy=CertificatePolicy(
                issuer_parameters=IssuerParameters(name="Self"),
                key_properties=KeyProperties(
                    exportable=True, key_type="RSA", key_size=2048, reuse_key=False,
                ),
                x509_certificate_properties=X509CertificateProperties(
                    subject="CN=TestSanURI",
                    subject_alternative_names=SubjectAlternativeNames(
                        uniform_resource_identifiers=["https://contoso.com", "spiffe://cluster/app"],
                    ),
                    validity_in_months=12,
                ),
            ),
        )

        try:
            client.create_certificate(cert_name, params)
            self._wait_for_operation(client, cert_name)

            policy = client.get_certificate_policy(cert_name)
            san = policy.x509_certificate_properties.subject_alternative_names
            assert san is not None
            assert san.uniform_resource_identifiers is not None
            assert set(san.uniform_resource_identifiers) == {"https://contoso.com", "spiffe://cluster/app"}
        finally:
            self._cleanup_cert(client, cert_name)

    @recorded_by_proxy
    def test_create_certificate_with_all_san_fields(self):
        """Create a self-signed cert with all SAN fields (existing + new) and verify."""
        client = self._create_client()
        cert_name = self.get_resource_name("livekvtestsanall")

        params = CertificateCreateParameters(
            certificate_policy=CertificatePolicy(
                issuer_parameters=IssuerParameters(name="Self"),
                key_properties=KeyProperties(
                    exportable=True, key_type="RSA", key_size=2048, reuse_key=False,
                ),
                x509_certificate_properties=X509CertificateProperties(
                    subject="CN=TestSanAll",
                    subject_alternative_names=SubjectAlternativeNames(
                        emails=["admin@contoso.com"],
                        dns_names=["contoso.com", "www.contoso.com"],
                        ip_addresses=["10.0.0.1", "2001:db8::1"],
                        uniform_resource_identifiers=["https://contoso.com/api"],
                    ),
                    validity_in_months=12,
                ),
            ),
        )

        try:
            client.create_certificate(cert_name, params)
            self._wait_for_operation(client, cert_name)

            policy = client.get_certificate_policy(cert_name)
            san = policy.x509_certificate_properties.subject_alternative_names
            assert san is not None

            assert san.emails is not None
            assert set(san.emails) == {"admin@contoso.com"}

            assert san.dns_names is not None
            assert set(san.dns_names) == {"contoso.com", "www.contoso.com"}

            assert san.ip_addresses is not None
            assert set(san.ip_addresses) == {"10.0.0.1", "2001:db8::1"}

            assert san.uniform_resource_identifiers is not None
            assert set(san.uniform_resource_identifiers) == {"https://contoso.com/api"}
        finally:
            self._cleanup_cert(client, cert_name)
