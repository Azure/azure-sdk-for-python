# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for PlatformManaged property on CertificatePolicy (2026-03-01-preview)."""

import pytest
from azure.keyvault.certificates._generated import models


class TestPlatformManagedModel:
    """Tests for the generated PlatformManaged model."""

    def test_platform_managed_with_certificate_usage(self):
        pm = models.PlatformManaged(certificate_usage="tls-server")
        assert pm.certificate_usage == "tls-server"
        assert pm.metadata is None

    def test_platform_managed_with_metadata(self):
        metadata = {"key1": "value1", "key2": 42}
        pm = models.PlatformManaged(certificate_usage="tls-client", metadata=metadata)
        assert pm.certificate_usage == "tls-client"
        assert pm.metadata == {"key1": "value1", "key2": 42}

    def test_platform_managed_empty_metadata(self):
        pm = models.PlatformManaged(certificate_usage="tls-server", metadata={})
        assert pm.certificate_usage == "tls-server"
        assert pm.metadata == {}

    def test_platform_managed_serialization_key(self):
        pm = models.PlatformManaged(certificate_usage="tls-server")
        serialized = dict(pm)
        assert "certificateUsage" in serialized
        assert serialized["certificateUsage"] == "tls-server"


class TestCertificatePolicyPlatformManaged:
    """Tests for platform_managed on the generated CertificatePolicy model."""

    def test_policy_with_platform_managed(self):
        pm = models.PlatformManaged(certificate_usage="tls-server")
        policy = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
            platform_managed=pm,
        )
        assert policy.platform_managed is not None
        assert policy.platform_managed.certificate_usage == "tls-server"

    def test_policy_platform_managed_none_by_default(self):
        policy = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
        )
        assert policy.platform_managed is None

    def test_policy_with_platform_managed_and_metadata(self):
        pm = models.PlatformManaged(
            certificate_usage="tls-client",
            metadata={"issuer": "internal-ca", "rotation_days": 90},
        )
        policy = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
            x509_certificate_properties=models.X509CertificateProperties(subject="CN=Test"),
            platform_managed=pm,
        )
        assert policy.platform_managed.certificate_usage == "tls-client"
        assert policy.platform_managed.metadata["issuer"] == "internal-ca"
        assert policy.platform_managed.metadata["rotation_days"] == 90

    def test_policy_serialization_includes_platform_managed(self):
        pm = models.PlatformManaged(certificate_usage="tls-server", metadata={"env": "prod"})
        policy = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
            platform_managed=pm,
        )
        serialized = dict(policy)
        assert "platformManaged" in serialized
        assert serialized["platformManaged"]["certificateUsage"] == "tls-server"
        assert serialized["platformManaged"]["metadata"] == {"env": "prod"}

    def test_policy_deserialization_with_platform_managed(self):
        raw = {
            "issuer": {"name": "Self"},
            "platformManaged": {
                "certificateUsage": "tls-server",
                "metadata": {"key": "value"},
            },
        }
        policy = models.CertificatePolicy(raw)
        assert policy.platform_managed is not None
        assert policy.platform_managed.certificate_usage == "tls-server"
        assert policy.platform_managed.metadata == {"key": "value"}

    def test_policy_deserialization_without_platform_managed(self):
        raw = {
            "issuer": {"name": "Self"},
            "x509_props": {"subject": "CN=Test"},
        }
        policy = models.CertificatePolicy(raw)
        assert policy.platform_managed is None
