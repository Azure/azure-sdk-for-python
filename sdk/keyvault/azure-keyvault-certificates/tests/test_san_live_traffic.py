# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Live traffic test for SubjectAlternativeNames IP address and URI support.

This script tests the SAN IP/URI feature against a real Azure Key Vault.
It follows the same test pattern used in the Java SDK live tests.

Prerequisites:
    - Azure CLI logged in (az login)
    - AZURE_KEYVAULT_URL environment variable set to a Key Vault URL
    - azure-keyvault-certificates package installed
    - azure-identity package installed
"""

import os
import sys
import time
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import (
    CertificateClient,
    CertificatePolicy,
    CertificateContentType,
    WellKnownIssuerNames,
)


def get_client():
    vault_url = os.environ.get("AZURE_KEYVAULT_URL")
    if not vault_url:
        print("ERROR: AZURE_KEYVAULT_URL environment variable not set")
        sys.exit(1)
    credential = DefaultAzureCredential()
    return CertificateClient(vault_url=vault_url, credential=credential)


def test_create_certificate_with_ip_addresses(client):
    """Test 1: Create certificate with IPv4 and IPv6 IP addresses in SANs."""
    cert_name = f"san-ip-test-{int(time.time()) % 10000}"
    print(f"\n=== Test 1: Create certificate with IP addresses ===")
    print(f"Certificate name: {cert_name}")

    policy = CertificatePolicy(
        issuer_name=WellKnownIssuerNames.self,
        subject=f"CN={cert_name}",
        san_ip_addresses=["10.0.0.1", "192.168.1.100"],
        content_type=CertificateContentType.pkcs12,
    )

    poller = client.begin_create_certificate(cert_name, policy)
    certificate = poller.result()
    print(f"Certificate created: {certificate.name}")

    # Retrieve and verify
    cert = client.get_certificate(cert_name)
    cert_policy = cert.policy
    print(f"  Subject: {cert_policy.subject}")
    print(f"  SAN IP Addresses: {cert_policy.san_ip_addresses}")

    assert cert_policy.san_ip_addresses is not None, "san_ip_addresses should not be None"
    assert len(cert_policy.san_ip_addresses) == 2, f"Expected 2 IPs, got {len(cert_policy.san_ip_addresses)}"
    assert "10.0.0.1" in cert_policy.san_ip_addresses, "10.0.0.1 not found in IPs"
    assert "192.168.1.100" in cert_policy.san_ip_addresses, "192.168.1.100 not found in IPs"

    print("  PASSED")
    return cert_name


def test_create_certificate_with_uris(client):
    """Test 2: Create certificate with URIs in SANs."""
    cert_name = f"san-uri-test-{int(time.time()) % 10000}"
    print(f"\n=== Test 2: Create certificate with URIs ===")
    print(f"Certificate name: {cert_name}")

    policy = CertificatePolicy(
        issuer_name=WellKnownIssuerNames.self,
        subject=f"CN={cert_name}",
        san_uris=["https://example.com/api", "spiffe://cluster.local/ns/default/sa/myapp"],
        content_type=CertificateContentType.pkcs12,
    )

    poller = client.begin_create_certificate(cert_name, policy)
    certificate = poller.result()
    print(f"Certificate created: {certificate.name}")

    # Retrieve and verify
    cert = client.get_certificate(cert_name)
    cert_policy = cert.policy
    print(f"  Subject: {cert_policy.subject}")
    print(f"  SAN URIs: {cert_policy.san_uris}")

    assert cert_policy.san_uris is not None, "san_uris should not be None"
    assert len(cert_policy.san_uris) == 2, f"Expected 2 URIs, got {len(cert_policy.san_uris)}"
    assert "https://example.com/api" in cert_policy.san_uris
    assert "spiffe://cluster.local/ns/default/sa/myapp" in cert_policy.san_uris

    print("  PASSED")
    return cert_name


def test_create_certificate_with_all_sans(client):
    """Test 3: Create certificate with all SAN types (emails, DNS, UPN, IPs, URIs)."""
    cert_name = f"san-all-test-{int(time.time()) % 10000}"
    print(f"\n=== Test 3: Create certificate with all SAN types ===")
    print(f"Certificate name: {cert_name}")

    policy = CertificatePolicy(
        issuer_name=WellKnownIssuerNames.self,
        subject=f"CN={cert_name}",
        san_emails=["test@example.com"],
        san_dns_names=["san-test.example.com"],
        san_user_principal_names=["user@contoso.onmicrosoft.com"],
        san_ip_addresses=["10.0.0.1", "2001:db8::1"],
        san_uris=["https://example.com/api"],
        content_type=CertificateContentType.pkcs12,
    )

    poller = client.begin_create_certificate(cert_name, policy)
    certificate = poller.result()
    print(f"Certificate created: {certificate.name}")

    # Retrieve and verify
    cert = client.get_certificate(cert_name)
    cp = cert.policy
    print(f"  Subject: {cp.subject}")
    print(f"  SAN emails: {cp.san_emails}")
    print(f"  SAN DNS names: {cp.san_dns_names}")
    print(f"  SAN UPNs: {cp.san_user_principal_names}")
    print(f"  SAN IP Addresses: {cp.san_ip_addresses}")
    print(f"  SAN URIs: {cp.san_uris}")

    assert cp.san_emails == ["test@example.com"]
    assert cp.san_dns_names == ["san-test.example.com"]
    assert cp.san_user_principal_names == ["user@contoso.onmicrosoft.com"]
    assert cp.san_ip_addresses is not None
    assert "10.0.0.1" in cp.san_ip_addresses
    assert "2001:db8::1" in cp.san_ip_addresses
    assert cp.san_uris == ["https://example.com/api"]

    print("  PASSED")
    return cert_name


def test_update_certificate_policy_with_ip_and_uri(client):
    """Test 4: Create then update certificate policy to add IP/URI SANs."""
    cert_name = f"san-update-test-{int(time.time()) % 10000}"
    print(f"\n=== Test 4: Update certificate policy with IP/URI SANs ===")
    print(f"Certificate name: {cert_name}")

    # Create with DNS SANs only
    policy = CertificatePolicy(
        issuer_name=WellKnownIssuerNames.self,
        subject=f"CN={cert_name}",
        san_dns_names=["original.example.com"],
        content_type=CertificateContentType.pkcs12,
    )

    poller = client.begin_create_certificate(cert_name, policy)
    poller.result()
    print(f"  Initial certificate created with DNS SANs")

    # Update the policy
    new_policy = CertificatePolicy(
        issuer_name=WellKnownIssuerNames.self,
        subject=f"CN={cert_name}",
        san_dns_names=["original.example.com"],
        san_ip_addresses=["172.16.0.1"],
        san_uris=["https://updated.example.com"],
        content_type=CertificateContentType.pkcs12,
    )
    client.update_certificate_policy(cert_name, new_policy)
    print(f"  Policy updated with IP and URI SANs")

    # Verify updated policy
    updated_policy = client.get_certificate_policy(cert_name)
    print(f"  Updated SAN IPs: {updated_policy.san_ip_addresses}")
    print(f"  Updated SAN URIs: {updated_policy.san_uris}")

    assert updated_policy.san_ip_addresses is not None
    assert "172.16.0.1" in updated_policy.san_ip_addresses
    assert updated_policy.san_uris is not None
    assert "https://updated.example.com" in updated_policy.san_uris

    print("  PASSED")
    return cert_name


def cleanup_certificates(client, cert_names):
    """Clean up test certificates."""
    print(f"\n=== Cleanup ===")
    for name in cert_names:
        try:
            poller = client.begin_delete_certificate(name)
            poller.wait()
            client.purge_deleted_certificate(name)
            print(f"  Deleted and purged: {name}")
        except Exception as e:
            print(f"  Failed to clean up {name}: {e}")


def main():
    print("=" * 60)
    print("Live Traffic Test: SAN IP Address and URI Support")
    print("=" * 60)

    client = get_client()
    print(f"Key Vault URL: {os.environ.get('AZURE_KEYVAULT_URL')}")

    cert_names = []
    passed = 0
    failed = 0

    tests = [
        test_create_certificate_with_ip_addresses,
        test_create_certificate_with_uris,
        test_create_certificate_with_all_sans,
        test_update_certificate_policy_with_ip_and_uri,
    ]

    for test_func in tests:
        try:
            cert_name = test_func(client)
            cert_names.append(cert_name)
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'=' * 60}")

    # Cleanup
    cleanup_certificates(client, cert_names)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
