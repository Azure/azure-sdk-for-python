# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider._request_tracing_context import RequestTracingContext
from azure.appconfiguration.provider._constants import (
    SNAPSHOT_REFERENCE_TAG,
    APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE,
    SNAPSHOT_REF_CONTENT_TYPE,
)


class TestSnapshotReferenceTracing:
    """Tests for snapshot reference request tracing functionality."""

    def test_request_tracing_context_initialization(self):
        """Test that request tracing context initializes snapshot reference tracking."""
        context = RequestTracingContext()

        # Should initialize with no snapshot reference usage
        assert context.uses_snapshot_reference is False

    def test_request_tracing_context_set_snapshot_reference_usage(self):
        """Test setting snapshot reference usage in tracing context."""
        context = RequestTracingContext()

        # Initially false
        assert context.uses_snapshot_reference is False

        # Set to true
        context.uses_snapshot_reference = True
        assert context.uses_snapshot_reference is True

        # Set back to false
        context.uses_snapshot_reference = False
        assert context.uses_snapshot_reference is False

    def test_correlation_context_header_without_snapshot_reference(self):
        """Test correlation context header when not using snapshot references."""
        context = RequestTracingContext()
        context.uses_snapshot_reference = False

        # Mock user agent
        with patch.object(context, "_user_agent", "test-user-agent"):
            header = context.get_correlation_context_header()

            # Should contain user agent but not snapshot reference tag
            assert "RequestType=Startup" in header
            assert SNAPSHOT_REFERENCE_TAG not in header

    def test_correlation_context_header_with_snapshot_reference(self):
        """Test correlation context header when using snapshot references."""
        context = RequestTracingContext()
        context.uses_snapshot_reference = True

        # Mock user agent
        with patch.object(context, "_user_agent", "test-user-agent"):
            header = context.get_correlation_context_header()

            # Should contain both user agent and snapshot reference tag
            assert "RequestType=Startup" in header
            assert SNAPSHOT_REFERENCE_TAG in header

    def test_snapshot_reference_detection_in_provider_base(self):
        """Test that snapshot reference detection works in provider base."""

        # Test with snapshot reference content type
        snapshot_ref_setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        assert (
            snapshot_ref_setting.content_type
            and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in snapshot_ref_setting.content_type
        )

        # Test with regular content type
        regular_setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        assert not (
            regular_setting.content_type and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in regular_setting.content_type
        )

    @patch(
        "azure.appconfiguration.provider._azureappconfigurationproviderbase.APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE",
        "test-profile",
    )
    def test_tracing_context_updated_during_processing(self, mock_profile):
        """Test that tracing context is updated when processing configuration with snapshot references."""
        from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
            _AzureAppConfigurationProviderBase,
        )

        # Create provider instance with mocked dependencies
        provider = _AzureAppConfigurationProviderBase()
        provider._request_tracing_context = RequestTracingContext()

        # Create a mock configuration setting with content type that will match the mock
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type='application/json; profile="test-profile"; charset=utf-8',
        )

        # Process the setting
        provider._process_key_value_base(setting, {})

        # Verify tracing context was updated
        assert provider._request_tracing_context.uses_snapshot_reference is True

    def test_tracing_context_not_updated_for_regular_settings(self):
        """Test that tracing context is not updated for regular settings."""
        from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
            _AzureAppConfigurationProviderBase,
        )

        # Create provider instance with mocked dependencies
        provider = _AzureAppConfigurationProviderBase()
        provider._request_tracing_context = RequestTracingContext()

        # Create a regular configuration setting
        setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        # Process the setting
        provider._process_key_value_base(setting, {})

        # Verify tracing context was not updated
        assert provider._request_tracing_context.uses_snapshot_reference is False

    def test_correlation_context_header_format_with_multiple_tags(self):
        """Test correlation context header format when multiple tags are present."""
        context = RequestTracingContext()
        context.uses_snapshot_reference = True

        # Mock user agent and other potential context
        with patch.object(context, "_user_agent", "test-user-agent"):
            header = context.get_correlation_context_header()

            # Verify the header contains expected components
            assert "RequestType=Startup" in header
            assert SNAPSHOT_REFERENCE_TAG in header

            # Verify format (tags should be comma-separated)
            tags = [tag.strip() for tag in header.split(",")]
            assert "RequestType=Startup" in tags
            assert SNAPSHOT_REFERENCE_TAG in tags

    def test_snapshot_reference_tag_constant(self):
        """Test that the snapshot reference tag constant has the expected value."""
        assert SNAPSHOT_REFERENCE_TAG == "UsesSnapshotReference=true"
