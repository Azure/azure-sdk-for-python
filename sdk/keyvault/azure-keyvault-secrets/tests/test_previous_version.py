# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import pytest

from azure.keyvault.secrets._generated.models._models import SecretBundle, DeletedSecretBundle
from azure.keyvault.secrets._models import SecretProperties, KeyVaultSecret, DeletedSecret


class TestPreviousVersion:
    """Tests for the previousVersion field on SecretBundle and SecretProperties."""

    def test_secret_bundle_deserializes_previous_version(self):
        """SecretBundle should deserialize previousVersion from JSON."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
            "previousVersion": "1",
        }
        bundle = SecretBundle(data)
        assert bundle.previous_version == "1"

    def test_secret_bundle_previous_version_none_when_absent(self):
        """SecretBundle.previous_version should be None when not in JSON."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
        }
        bundle = SecretBundle(data)
        assert bundle.previous_version is None

    def test_deleted_secret_bundle_deserializes_previous_version(self):
        """DeletedSecretBundle should deserialize previousVersion from JSON."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
            "previousVersion": "1",
            "recoveryId": "https://myvault.vault.azure.net/deletedsecrets/mySecret",
        }
        bundle = DeletedSecretBundle(data)
        assert bundle.previous_version == "1"

    def test_secret_properties_from_secret_bundle(self):
        """SecretProperties._from_secret_bundle should map previous_version."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
            "previousVersion": "1",
        }
        bundle = SecretBundle(data)
        props = SecretProperties._from_secret_bundle(bundle)
        assert props.previous_version == "1"

    def test_secret_properties_previous_version_none(self):
        """SecretProperties.previous_version should be None when absent."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
        }
        bundle = SecretBundle(data)
        props = SecretProperties._from_secret_bundle(bundle)
        assert props.previous_version is None

    def test_key_vault_secret_from_secret_bundle(self):
        """KeyVaultSecret._from_secret_bundle should carry previous_version."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
            "previousVersion": "1",
        }
        bundle = SecretBundle(data)
        secret = KeyVaultSecret._from_secret_bundle(bundle)
        assert secret.properties.previous_version == "1"

    def test_deleted_secret_from_deleted_secret_bundle(self):
        """DeletedSecret._from_deleted_secret_bundle should carry previous_version."""
        data = {
            "id": "https://myvault.vault.azure.net/secrets/mySecret/2",
            "value": "secret-value",
            "previousVersion": "1",
            "recoveryId": "https://myvault.vault.azure.net/deletedsecrets/mySecret",
        }
        bundle = DeletedSecretBundle(data)
        deleted = DeletedSecret._from_deleted_secret_bundle(bundle)
        assert deleted.properties.previous_version == "1"
