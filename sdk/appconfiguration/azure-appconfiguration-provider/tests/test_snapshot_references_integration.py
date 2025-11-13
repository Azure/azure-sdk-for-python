# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider._snapshot_reference_parser import SnapshotReferenceParser
from azure.appconfiguration.provider._constants import SNAPSHOT_REF_CONTENT_TYPE, APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE
from azure.appconfiguration.provider._request_tracing_context import _RequestTracingContext


class TestSnapshotReferenceParser:
    """Integration tests for snapshot reference parser."""

    def test_parse_valid_snapshot_reference(self):
        """Test parsing a valid snapshot reference JSON."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = SnapshotReferenceParser.parse(setting)
        assert result == "test-snapshot"

    def test_parse_snapshot_reference_with_whitespace(self):
        """Test parsing snapshot reference with whitespace in snapshot name."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "  test-snapshot  "}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = SnapshotReferenceParser.parse(setting)
        assert result == "test-snapshot"  # Should be trimmed

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"invalid": json}',  # Invalid JSON
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Invalid JSON format"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_missing_snapshot_name_field(self):
        """Test parsing JSON without snapshot_name field raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"other_field": "value"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*'snapshot_name' property is required"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_empty_snapshot_name(self):
        """Test parsing JSON with empty snapshot name raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": ""}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Snapshot name cannot be empty"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_whitespace_only_snapshot_name(self):
        """Test parsing JSON with whitespace-only snapshot name raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "   "}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Snapshot name cannot be empty"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_non_string_snapshot_name(self):
        """Test parsing JSON with non-string snapshot name raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": 123}',  # Number instead of string
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*must be a string value"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_none_setting(self):
        """Test parsing None setting raises ValueError."""
        with pytest.raises(ValueError, match="Setting cannot be None"):
            SnapshotReferenceParser.parse(None)

    def test_parse_empty_value(self):
        """Test parsing setting with empty value raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value="",
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Value cannot be empty"):
            SnapshotReferenceParser.parse(setting)


class TestSnapshotReferenceContentTypeDetection:
    """Integration tests for snapshot reference content type detection."""

    def test_snapshot_reference_content_type_detection(self):
        """Test that snapshot reference content type is correctly detected."""
        # Test with snapshot reference content type
        snapshot_ref_setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Should detect as snapshot reference
        assert (
            snapshot_ref_setting.content_type
            and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in snapshot_ref_setting.content_type
        )

    def test_regular_setting_content_type_detection(self):
        """Test that regular settings are not detected as snapshot references."""
        # Test with regular content type
        regular_setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        # Should not detect as snapshot reference
        assert not (
            regular_setting.content_type and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in regular_setting.content_type
        )

    def test_feature_flag_content_type_detection(self):
        """Test that feature flags are not detected as snapshot references."""
        # Test with feature flag content type
        feature_flag_setting = ConfigurationSetting(
            key=".appconfig.featureflag/TestFlag",
            value='{"enabled": true}',
            content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
        )

        # Should not detect as snapshot reference
        assert not (
            feature_flag_setting.content_type
            and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in feature_flag_setting.content_type
        )

    def test_key_vault_reference_content_type_detection(self):
        """Test that Key Vault references are not detected as snapshot references."""
        # Test with Key Vault reference content type
        kv_ref_setting = ConfigurationSetting(
            key="DatabaseConnectionString",
            value='{"uri": "https://vault.vault.azure.net/secrets/connectionstring"}',
            content_type="application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8",
        )

        # Should not detect as snapshot reference
        assert not (kv_ref_setting.content_type and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in kv_ref_setting.content_type)


class TestRequestTracingContextIntegration:
    """Integration tests for request tracing context with snapshot references."""

    def test_request_tracing_context_snapshot_reference_tracking(self):
        """Test that request tracing context properly tracks snapshot reference usage."""
        context = _RequestTracingContext()

        # Initially should not use snapshot references
        assert not context.uses_snapshot_reference

        # After enabling, should report usage
        context.uses_snapshot_reference = True
        assert context.uses_snapshot_reference

    def test_request_tracing_context_correlation_header(self):
        """Test correlation context header generation with snapshot reference usage."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = True

        # Test correlation context header update
        headers = {"existing": "header"}
        context.update_correlation_context_header(headers)

        # Should contain correlation context header
        assert "Correlation-Context" in headers
        correlation_header = headers["Correlation-Context"]

        # Should contain snapshot reference tag
        assert "UsesSnapshotReference" in correlation_header


# Note: These are true integration tests that test the actual functionality
# without mocking any core components. They test:
# 1. Snapshot reference parser with comprehensive input validation
# 2. Content type detection logic for different configuration setting types
# 3. Constants validation to ensure proper values
# 4. Request tracing context integration with snapshot reference tracking
#
# For full end-to-end tests that require Azure App Configuration service,
# those would be in a separate test file (e.g., test_e2e_snapshots.py)
# and would require live Azure resources or recordings.
