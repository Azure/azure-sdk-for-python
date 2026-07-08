# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for SubjectAlternativeNames IP address and URI support in CertificatePolicy."""

import pytest
from azure.keyvault.certificates import CertificatePolicy
from azure.keyvault.certificates._generated import models


class TestSanIpAddresses:
    """Tests for san_ip_addresses property on CertificatePolicy."""

    def test_san_ip_addresses_ipv4(self):
        policy = CertificatePolicy(issuer_name="Self", san_ip_addresses=["192.168.1.1"])
        assert policy.san_ip_addresses == ["192.168.1.1"]

    def test_san_ip_addresses_ipv6(self):
        policy = CertificatePolicy(issuer_name="Self", san_ip_addresses=["::1", "2001:db8::1"])
        assert policy.san_ip_addresses == ["::1", "2001:db8::1"]

    def test_san_ip_addresses_mixed(self):
        ips = ["192.168.1.1", "10.0.0.1", "::1", "2001:db8::1"]
        policy = CertificatePolicy(issuer_name="Self", san_ip_addresses=ips)
        assert policy.san_ip_addresses == ips

    def test_san_ip_addresses_none_by_default(self):
        policy = CertificatePolicy(issuer_name="Self", subject="CN=Test")
        assert policy.san_ip_addresses is None

    def test_san_ip_addresses_empty_list_treated_as_none(self):
        policy = CertificatePolicy(issuer_name="Self", san_ip_addresses=[])
        assert policy.san_ip_addresses is None


class TestSanUris:
    """Tests for san_uris property on CertificatePolicy."""

    def test_san_uris_https(self):
        policy = CertificatePolicy(issuer_name="Self", san_uris=["https://example.com"])
        assert policy.san_uris == ["https://example.com"]

    def test_san_uris_multiple(self):
        uris = ["https://example.com", "https://api.example.com/v1"]
        policy = CertificatePolicy(issuer_name="Self", san_uris=uris)
        assert policy.san_uris == uris

    def test_san_uris_none_by_default(self):
        policy = CertificatePolicy(issuer_name="Self", subject="CN=Test")
        assert policy.san_uris is None

    def test_san_uris_empty_list_treated_as_none(self):
        policy = CertificatePolicy(issuer_name="Self", san_uris=[])
        assert policy.san_uris is None


class TestSanCombinations:
    """Tests for combining san_ip_addresses and san_uris with other SAN fields."""

    def test_all_san_fields_together(self):
        policy = CertificatePolicy(
            issuer_name="Self",
            subject="CN=Test",
            san_emails=["test@example.com"],
            san_dns_names=["test.example.com"],
            san_user_principal_names=["user@example.com"],
            san_ip_addresses=["192.168.1.1"],
            san_uris=["https://example.com"],
        )
        assert policy.san_emails == ["test@example.com"]
        assert policy.san_dns_names == ["test.example.com"]
        assert policy.san_user_principal_names == ["user@example.com"]
        assert policy.san_ip_addresses == ["192.168.1.1"]
        assert policy.san_uris == ["https://example.com"]

    def test_ip_and_uri_only_no_subject(self):
        policy = CertificatePolicy(
            issuer_name="Self",
            san_ip_addresses=["10.0.0.1"],
            san_uris=["https://example.com"],
        )
        assert policy.san_ip_addresses == ["10.0.0.1"]
        assert policy.san_uris == ["https://example.com"]
        assert policy.subject is None


class TestSanSerialization:
    """Tests for serialization/deserialization of IP addresses and URIs through the generated model."""

    def test_to_bundle_includes_ip_addresses(self):
        policy = CertificatePolicy(
            issuer_name="Self",
            san_ip_addresses=["192.168.1.1", "::1"],
        )
        bundle = policy._to_certificate_policy_bundle()
        sans = bundle.x509_certificate_properties.subject_alternative_names
        assert sans.ip_addresses == ["192.168.1.1", "::1"]

    def test_to_bundle_includes_uris(self):
        policy = CertificatePolicy(
            issuer_name="Self",
            san_uris=["https://example.com"],
        )
        bundle = policy._to_certificate_policy_bundle()
        sans = bundle.x509_certificate_properties.subject_alternative_names
        assert sans.uris == ["https://example.com"]

    def test_to_bundle_all_sans(self):
        policy = CertificatePolicy(
            issuer_name="Self",
            san_emails=["test@example.com"],
            san_dns_names=["test.com"],
            san_user_principal_names=["user@example.com"],
            san_ip_addresses=["10.0.0.1"],
            san_uris=["https://example.com"],
        )
        bundle = policy._to_certificate_policy_bundle()
        sans = bundle.x509_certificate_properties.subject_alternative_names
        assert sans.emails == ["test@example.com"]
        assert sans.dns_names == ["test.com"]
        assert sans.upns == ["user@example.com"]
        assert sans.ip_addresses == ["10.0.0.1"]
        assert sans.uris == ["https://example.com"]

    def test_from_bundle_with_ip_addresses(self):
        bundle = models.CertificatePolicy(
            x509_certificate_properties=models.X509CertificateProperties(
                subject_alternative_names=models.SubjectAlternativeNames(
                    ip_addresses=["192.168.1.1", "2001:db8::1"],
                )
            ),
            issuer_parameters=models.IssuerParameters(name="Self"),
        )
        policy = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert policy.san_ip_addresses == ["192.168.1.1", "2001:db8::1"]

    def test_from_bundle_with_uris(self):
        bundle = models.CertificatePolicy(
            x509_certificate_properties=models.X509CertificateProperties(
                subject_alternative_names=models.SubjectAlternativeNames(
                    uris=["https://example.com", "https://api.example.com"],
                )
            ),
            issuer_parameters=models.IssuerParameters(name="Self"),
        )
        policy = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert policy.san_uris == ["https://example.com", "https://api.example.com"]

    def test_from_bundle_no_sans(self):
        bundle = models.CertificatePolicy(
            x509_certificate_properties=models.X509CertificateProperties(subject="CN=Test"),
            issuer_parameters=models.IssuerParameters(name="Self"),
        )
        policy = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert policy.san_ip_addresses is None
        assert policy.san_uris is None

    def test_from_bundle_none_policy(self):
        policy = CertificatePolicy._from_certificate_policy_bundle(None)
        assert policy.san_ip_addresses is None
        assert policy.san_uris is None

    def test_roundtrip_ip_addresses_and_uris(self):
        original = CertificatePolicy(
            issuer_name="Self",
            subject="CN=Test",
            san_ip_addresses=["192.168.1.1", "::1"],
            san_uris=["https://example.com"],
            san_emails=["test@example.com"],
            san_dns_names=["test.com"],
        )
        bundle = original._to_certificate_policy_bundle()
        restored = CertificatePolicy._from_certificate_policy_bundle(bundle)

        assert restored.san_ip_addresses == original.san_ip_addresses
        assert restored.san_uris == original.san_uris
        assert restored.san_emails == original.san_emails
        assert restored.san_dns_names == original.san_dns_names
        assert restored.subject == original.subject
        assert restored.issuer_name == original.issuer_name


class TestSubjectAlternativeNamesModel:
    """Tests for the generated SubjectAlternativeNames model directly."""

    def test_model_has_ip_addresses_field(self):
        sans = models.SubjectAlternativeNames(ip_addresses=["192.168.1.1"])
        assert sans.ip_addresses == ["192.168.1.1"]

    def test_model_has_uris_field(self):
        sans = models.SubjectAlternativeNames(uris=["https://example.com"])
        assert sans.uris == ["https://example.com"]

    def test_model_all_fields(self):
        sans = models.SubjectAlternativeNames(
            emails=["test@example.com"],
            dns_names=["test.com"],
            upns=["user@example.com"],
            ip_addresses=["10.0.0.1"],
            uris=["https://example.com"],
        )
        assert sans.emails == ["test@example.com"]
        assert sans.dns_names == ["test.com"]
        assert sans.upns == ["user@example.com"]
        assert sans.ip_addresses == ["10.0.0.1"]
        assert sans.uris == ["https://example.com"]

    def test_model_ip_addresses_serialization_key(self):
        sans = models.SubjectAlternativeNames(ip_addresses=["192.168.1.1"])
        # Verify the JSON field name is "ipAddresses" (camelCase)
        serialized = dict(sans)
        assert "ipAddresses" in serialized
        assert serialized["ipAddresses"] == ["192.168.1.1"]
