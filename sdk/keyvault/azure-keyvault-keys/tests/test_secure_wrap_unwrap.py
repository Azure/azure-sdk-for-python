# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore KWPAD Vtbw kwpad vtbw
"""
Unit tests for the new ``securewrapkey`` / ``secureunwrapkey`` operations
added in service API version ``2026-03-01-preview``.

These tests cover model construction, request body serialization, and a
verification that the generated client exposes the new operations. A live
end-to-end recording requires a Managed HSM with ``secureWrap`` enabled (not
available in our test subscription) and is tracked as a follow-up — the same
gap that caused the Go SDK to skip its TestSecureWrapUnwrapKey live test.
"""
import inspect

import pytest

from azure.keyvault.keys._generated import KeyVaultClient
from azure.keyvault.keys._generated import models as _models


class TestSecureWrapUnwrapOperations:
    """The generated client should expose the new operations on both sync and async."""

    def test_sync_secure_wrap_key_exists(self):
        from azure.keyvault.keys._generated._operations._operations import (
            _KeyVaultClientOperationsMixin,
        )

        assert hasattr(_KeyVaultClientOperationsMixin, "secure_wrap_key")
        sig = inspect.signature(_KeyVaultClientOperationsMixin.secure_wrap_key)
        params = list(sig.parameters)
        assert "key_name" in params
        assert "key_version" in params
        assert "parameters" in params

    def test_sync_secure_unwrap_key_exists(self):
        from azure.keyvault.keys._generated._operations._operations import (
            _KeyVaultClientOperationsMixin,
        )

        assert hasattr(_KeyVaultClientOperationsMixin, "secure_unwrap_key")
        sig = inspect.signature(_KeyVaultClientOperationsMixin.secure_unwrap_key)
        params = list(sig.parameters)
        assert "key_name" in params
        assert "key_version" in params
        assert "parameters" in params

    def test_async_secure_wrap_key_exists(self):
        from azure.keyvault.keys._generated.aio._operations._operations import (
            _KeyVaultClientOperationsMixin as AsyncMixin,
        )

        assert hasattr(AsyncMixin, "secure_wrap_key")
        assert inspect.iscoroutinefunction(AsyncMixin.secure_wrap_key)

    def test_async_secure_unwrap_key_exists(self):
        from azure.keyvault.keys._generated.aio._operations._operations import (
            _KeyVaultClientOperationsMixin as AsyncMixin,
        )

        assert hasattr(AsyncMixin, "secure_unwrap_key")
        assert inspect.iscoroutinefunction(AsyncMixin.secure_unwrap_key)


class TestSecureWrapUnwrapModels:
    """Tests for the new generated model types."""

    def test_wrap_parameters_required_algorithm(self):
        p = _models.SecureKeyWrapOperationParameters(algorithm="RSA-OAEP-256")
        assert p.algorithm == "RSA-OAEP-256"

    def test_unwrap_parameters_required_fields(self):
        p = _models.SecureKeyUnWrapOperationParameters(
            algorithm="RSA-OAEP-256",
            value=b"wrapped",
        )
        assert p.algorithm == "RSA-OAEP-256"
        assert p.value == b"wrapped"

    def test_secure_key_operation_result_shape(self):
        raw = {
            "kid": "https://v.vault.azure.net/keys/k/v",
            "value": "ZGVtbw==",
            "alg": "RSA-OAEP-256",
        }
        result = _models.SecureKeyOperationResult(raw)
        assert result.kid == "https://v.vault.azure.net/keys/k/v"
        assert result.algorithm == "RSA-OAEP-256"

    @pytest.mark.parametrize(
        "expected",
        ["RSA-OAEP-256", "A128KW", "A192KW", "A256KW", "A128KWPAD", "A192KWPAD", "A256KWPAD"],
    )
    def test_wrap_algorithm_enum_has_known_wire_value(self, expected):
        """JsonWebKeyWrapAlgorithm members should serialize to the spec wire values."""
        wire_values = {m.value for m in _models.JsonWebKeyWrapAlgorithm}
        assert expected in wire_values, f"missing wire value {expected}; have {sorted(wire_values)}"

    def test_wrap_parameters_serialization_omits_value(self):
        """secure_wrap_key takes only an algorithm — no value to wrap."""
        p = _models.SecureKeyWrapOperationParameters(algorithm="A256KWPAD")
        serialized = dict(p)
        assert serialized.get("alg") == "A256KWPAD"
        assert "value" not in serialized

    def test_unwrap_parameters_serialization_includes_value(self):
        p = _models.SecureKeyUnWrapOperationParameters(
            algorithm="RSA-OAEP-256",
            value=b"wrapped-bytes",
        )
        serialized = dict(p)
        assert serialized.get("alg") == "RSA-OAEP-256"
        # Value is base64url-encoded on the wire
        assert serialized.get("value") is not None


class TestKeyVaultClientApiVersion:
    """Default api-version should be the new preview."""

    def test_default_api_version_is_2026_03_01_preview(self):
        from azure.keyvault.keys._generated._configuration import KeyVaultClientConfiguration

        creds = type("FakeCred", (), {"get_token": lambda *a, **kw: None})()
        cfg = KeyVaultClientConfiguration(vault_base_url="https://x.vault.azure.net", credential=creds)
        assert cfg.api_version == "2026-03-01-preview"
