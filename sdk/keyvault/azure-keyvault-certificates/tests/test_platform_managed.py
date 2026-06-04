# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for PlatformManaged property on CertificatePolicy (2026-03-01-preview)."""

import pytest
from azure.keyvault.certificates import CertificatePolicy, PlatformManaged, WellKnownIssuerNames
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
        }
        policy = models.CertificatePolicy(raw)
        assert policy.platform_managed is None


class TestPublicPlatformManaged:
    """Tests for the public PlatformManaged wrapper and CertificatePolicy.platform_managed."""

    def test_wrapper_required_field_only(self):
        pm = PlatformManaged("tls-server")
        assert pm.certificate_usage == "tls-server"
        assert pm.metadata is None

    def test_wrapper_with_metadata(self):
        pm = PlatformManaged("tls-client", metadata={"env": "prod"})
        assert pm.certificate_usage == "tls-client"
        assert pm.metadata == {"env": "prod"}

    def test_wrapper_repr(self):
        pm = PlatformManaged("tls-server")
        assert "tls-server" in repr(pm)

    def test_metadata_kwarg_only(self):
        # metadata must be keyword-only
        with pytest.raises(TypeError):
            PlatformManaged("tls-server", {"env": "prod"})  # type: ignore

    def test_policy_default_platform_managed_is_none(self):
        policy = CertificatePolicy(issuer_name=WellKnownIssuerNames.self)
        assert policy.platform_managed is None

    def test_policy_with_platform_managed(self):
        pm = PlatformManaged("tls-server", metadata={"k": "v"})
        policy = CertificatePolicy(issuer_name=WellKnownIssuerNames.self, platform_managed=pm)
        assert policy.platform_managed is pm
        assert policy.platform_managed.certificate_usage == "tls-server"
        assert policy.platform_managed.metadata == {"k": "v"}

    def test_to_bundle_serializes_platform_managed(self):
        pm = PlatformManaged("tls-server", metadata={"env": "prod"})
        policy = CertificatePolicy(issuer_name="Self", platform_managed=pm)
        bundle = policy._to_certificate_policy_bundle()
        assert bundle.platform_managed is not None
        assert bundle.platform_managed.certificate_usage == "tls-server"
        assert bundle.platform_managed.metadata == {"env": "prod"}

    def test_to_bundle_without_platform_managed(self):
        policy = CertificatePolicy(issuer_name="Self")
        bundle = policy._to_certificate_policy_bundle()
        assert bundle.platform_managed is None

    def test_from_bundle_reads_platform_managed(self):
        gen_pm = models.PlatformManaged(certificate_usage="tls-client", metadata={"a": 1})
        bundle = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
            platform_managed=gen_pm,
        )
        policy = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert policy.platform_managed is not None
        assert policy.platform_managed.certificate_usage == "tls-client"
        assert policy.platform_managed.metadata == {"a": 1}

    def test_from_bundle_without_platform_managed(self):
        bundle = models.CertificatePolicy(
            issuer_parameters=models.IssuerParameters(name="Self"),
        )
        policy = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert policy.platform_managed is None

    def test_round_trip_preserves_platform_managed(self):
        pm = PlatformManaged("tls-server", metadata={"env": "prod", "owner": "team-x"})
        original = CertificatePolicy(issuer_name="Self", platform_managed=pm)
        bundle = original._to_certificate_policy_bundle()
        restored = CertificatePolicy._from_certificate_policy_bundle(bundle)
        assert restored.platform_managed is not None
        assert restored.platform_managed.certificate_usage == "tls-server"
        assert restored.platform_managed.metadata == {"env": "prod", "owner": "team-x"}

    def test_platform_managed_exported_from_public_namespace(self):
        # Guards against future regression where the wrapper is only available under _models.
        import azure.keyvault.certificates as kv_certs

        assert kv_certs.PlatformManaged is PlatformManaged
        assert "PlatformManaged" in kv_certs.__all__
