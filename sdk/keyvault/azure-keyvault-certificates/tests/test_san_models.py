# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for SubjectAlternativeNames model — new ip_addresses and
uniform_resource_identifiers fields added in API version 2025-07-01."""

import pytest
from azure.keyvault.certificates._generated.models import (
    CertificateCreateParameters,
    CertificatePolicy,
    IssuerParameters,
    SubjectAlternativeNames,
    X509CertificateProperties,
)


class TestSubjectAlternativeNamesModel:
    """Tests for the SubjectAlternativeNames model focusing on the new
    ip_addresses and uniform_resource_identifiers fields."""

    # ---- construction with keyword arguments ----

    def test_ip_addresses_only(self):
        san = SubjectAlternativeNames(ip_addresses=["10.0.0.1", "192.168.1.100"])
        assert san.ip_addresses == ["10.0.0.1", "192.168.1.100"]
        assert san.uniform_resource_identifiers is None
        assert san.emails is None
        assert san.dns_names is None
        assert san.upns is None

    def test_uniform_resource_identifiers_only(self):
        uris = ["https://example.com", "spiffe://cluster.local/ns/default/sa/app"]
        san = SubjectAlternativeNames(uniform_resource_identifiers=uris)
        assert san.uniform_resource_identifiers == uris
        assert san.ip_addresses is None
        assert san.emails is None

    def test_both_new_fields(self):
        san = SubjectAlternativeNames(
            ip_addresses=["10.0.0.1", "fd00::1"],
            uniform_resource_identifiers=["https://example.com"],
        )
        assert san.ip_addresses == ["10.0.0.1", "fd00::1"]
        assert san.uniform_resource_identifiers == ["https://example.com"]

    def test_all_fields(self):
        san = SubjectAlternativeNames(
            emails=["admin@contoso.com"],
            dns_names=["contoso.com", "www.contoso.com"],
            upns=["admin@contoso.com"],
            ip_addresses=["10.0.0.1", "2001:db8::1"],
            uniform_resource_identifiers=["https://contoso.com/app"],
        )
        assert san.emails == ["admin@contoso.com"]
        assert san.dns_names == ["contoso.com", "www.contoso.com"]
        assert san.upns == ["admin@contoso.com"]
        assert san.ip_addresses == ["10.0.0.1", "2001:db8::1"]
        assert san.uniform_resource_identifiers == ["https://contoso.com/app"]

    def test_ipv6_addresses(self):
        ipv6 = ["::1", "fe80::1", "2001:db8:85a3::8a2e:370:7334"]
        san = SubjectAlternativeNames(ip_addresses=ipv6)
        assert san.ip_addresses == ipv6

    def test_empty_lists(self):
        san = SubjectAlternativeNames(ip_addresses=[], uniform_resource_identifiers=[])
        assert san.ip_addresses == []
        assert san.uniform_resource_identifiers == []

    # ---- serialization (as_dict) verifying REST wire names ----

    def test_ip_addresses_serialization(self):
        san = SubjectAlternativeNames(ip_addresses=["10.0.0.1"])
        d = san.as_dict()
        assert "ipAddresses" in d
        assert d["ipAddresses"] == ["10.0.0.1"]
        # Python attr name should NOT be in the wire dict
        assert "ip_addresses" not in d

    def test_uniform_resource_identifiers_serialization(self):
        san = SubjectAlternativeNames(uniform_resource_identifiers=["https://example.com"])
        d = san.as_dict()
        assert "uris" in d
        assert d["uris"] == ["https://example.com"]
        assert "uniform_resource_identifiers" not in d

    def test_all_fields_serialization(self):
        san = SubjectAlternativeNames(
            emails=["a@b.com"],
            dns_names=["b.com"],
            upns=["u@b.com"],
            ip_addresses=["10.0.0.1"],
            uniform_resource_identifiers=["https://b.com"],
        )
        d = san.as_dict()
        assert d["emails"] == ["a@b.com"]
        assert d["dns_names"] == ["b.com"]
        assert d["upns"] == ["u@b.com"]
        assert d["ipAddresses"] == ["10.0.0.1"]
        assert d["uris"] == ["https://b.com"]

    # ---- deserialization from dict (mapping / JSON-like input) ----

    def test_deserialize_ip_addresses(self):
        data = {"ipAddresses": ["10.0.0.1", "192.168.0.1"]}
        san = SubjectAlternativeNames(data)
        assert san.ip_addresses == ["10.0.0.1", "192.168.0.1"]

    def test_deserialize_uniform_resource_identifiers(self):
        data = {"uris": ["https://example.com", "urn:example:resource"]}
        san = SubjectAlternativeNames(data)
        assert san.uniform_resource_identifiers == ["https://example.com", "urn:example:resource"]

    def test_deserialize_all_fields(self):
        data = {
            "emails": ["x@y.com"],
            "dns_names": ["y.com"],
            "upns": ["x@y.com"],
            "ipAddresses": ["10.0.0.1"],
            "uris": ["https://y.com"],
        }
        san = SubjectAlternativeNames(data)
        assert san.emails == ["x@y.com"]
        assert san.dns_names == ["y.com"]
        assert san.upns == ["x@y.com"]
        assert san.ip_addresses == ["10.0.0.1"]
        assert san.uniform_resource_identifiers == ["https://y.com"]

    # ---- round-trip: construct → as_dict → construct → compare ----

    def test_round_trip(self):
        original = SubjectAlternativeNames(
            emails=["admin@contoso.com"],
            dns_names=["contoso.com"],
            upns=["admin@contoso.com"],
            ip_addresses=["10.0.0.1", "fd00::1"],
            uniform_resource_identifiers=["https://contoso.com"],
        )
        wire = original.as_dict()
        restored = SubjectAlternativeNames(wire)
        assert restored.emails == original.emails
        assert restored.dns_names == original.dns_names
        assert restored.upns == original.upns
        assert restored.ip_addresses == original.ip_addresses
        assert restored.uniform_resource_identifiers == original.uniform_resource_identifiers

    # ---- nested in X509CertificateProperties ----

    def test_san_in_x509_properties(self):
        san = SubjectAlternativeNames(
            ip_addresses=["10.0.0.1"],
            uniform_resource_identifiers=["https://contoso.com"],
        )
        x509 = X509CertificateProperties(
            subject="CN=TestCert",
            subject_alternative_names=san,
            validity_in_months=12,
        )
        assert x509.subject_alternative_names is not None
        assert x509.subject_alternative_names.ip_addresses == ["10.0.0.1"]
        assert x509.subject_alternative_names.uniform_resource_identifiers == ["https://contoso.com"]

    def test_san_in_x509_serialization(self):
        san = SubjectAlternativeNames(
            dns_names=["contoso.com"],
            ip_addresses=["10.0.0.1"],
            uniform_resource_identifiers=["https://contoso.com"],
        )
        x509 = X509CertificateProperties(
            subject="CN=TestCert",
            subject_alternative_names=san,
        )
        d = x509.as_dict()
        assert "sans" in d
        assert d["sans"]["ipAddresses"] == ["10.0.0.1"]
        assert d["sans"]["uris"] == ["https://contoso.com"]
        assert d["sans"]["dns_names"] == ["contoso.com"]

    # ---- nested in full CertificatePolicy ----

    def test_san_in_certificate_policy(self):
        san = SubjectAlternativeNames(
            ip_addresses=["10.0.0.1", "192.168.1.1"],
            uniform_resource_identifiers=["https://contoso.com/api"],
            dns_names=["api.contoso.com"],
        )
        policy = CertificatePolicy(
            issuer_parameters=IssuerParameters(name="Self"),
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=TestCert",
                subject_alternative_names=san,
                validity_in_months=12,
            ),
        )
        result_san = policy.x509_certificate_properties.subject_alternative_names
        assert result_san.ip_addresses == ["10.0.0.1", "192.168.1.1"]
        assert result_san.uniform_resource_identifiers == ["https://contoso.com/api"]
        assert result_san.dns_names == ["api.contoso.com"]

    def test_certificate_policy_serialization(self):
        san = SubjectAlternativeNames(
            ip_addresses=["10.0.0.1"],
            uniform_resource_identifiers=["https://contoso.com"],
        )
        policy = CertificatePolicy(
            issuer_parameters=IssuerParameters(name="Self"),
            x509_certificate_properties=X509CertificateProperties(
                subject="CN=TestCert",
                subject_alternative_names=san,
                validity_in_months=12,
            ),
        )
        d = policy.as_dict()
        sans_dict = d["x509_props"]["sans"]
        assert sans_dict["ipAddresses"] == ["10.0.0.1"]
        assert sans_dict["uris"] == ["https://contoso.com"]

    # ---- full CertificateCreateParameters with new SAN fields ----

    def test_create_parameters_with_san(self):
        params = CertificateCreateParameters(
            certificate_policy=CertificatePolicy(
                issuer_parameters=IssuerParameters(name="Self"),
                x509_certificate_properties=X509CertificateProperties(
                    subject="CN=TestCert",
                    subject_alternative_names=SubjectAlternativeNames(
                        dns_names=["test.contoso.com"],
                        ip_addresses=["10.0.0.1", "2001:db8::1"],
                        uniform_resource_identifiers=["https://contoso.com", "spiffe://cluster/app"],
                    ),
                    validity_in_months=12,
                ),
            ),
        )
        d = params.as_dict()
        sans = d["policy"]["x509_props"]["sans"]
        assert sans["dns_names"] == ["test.contoso.com"]
        assert sans["ipAddresses"] == ["10.0.0.1", "2001:db8::1"]
        assert sans["uris"] == ["https://contoso.com", "spiffe://cluster/app"]

    def test_create_parameters_deserialization_round_trip(self):
        """Verify that JSON from the wire can round-trip through models."""
        wire_json = {
            "policy": {
                "issuer": {"name": "Self"},
                "x509_props": {
                    "subject": "CN=TestCert",
                    "sans": {
                        "dns_names": ["test.contoso.com"],
                        "ipAddresses": ["10.0.0.1"],
                        "uris": ["https://contoso.com"],
                        "emails": ["admin@contoso.com"],
                        "upns": ["admin@contoso.com"],
                    },
                    "validity_months": 12,
                },
            },
        }
        params = CertificateCreateParameters(wire_json)
        san = params.certificate_policy.x509_certificate_properties.subject_alternative_names
        assert san.dns_names == ["test.contoso.com"]
        assert san.ip_addresses == ["10.0.0.1"]
        assert san.uniform_resource_identifiers == ["https://contoso.com"]
        assert san.emails == ["admin@contoso.com"]
        assert san.upns == ["admin@contoso.com"]
