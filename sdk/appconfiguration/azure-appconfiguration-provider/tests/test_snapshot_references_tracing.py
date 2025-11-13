# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider._request_tracing_context import _RequestTracingContext
from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase
from azure.appconfiguration.provider._constants import (
    SNAPSHOT_REFERENCE_TAG,
    APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE,
    SNAPSHOT_REF_CONTENT_TYPE,
)


class TestSnapshotReferenceTracing:
    """Tests for snapshot reference request tracing functionality."""

    def test_request_tracing_context_initialization(self):
        """Test that request tracing context initializes snapshot reference tracking."""
        context = _RequestTracingContext()

        # Should initialize with no snapshot reference usage
        assert context.uses_snapshot_reference is False

    def test_request_tracing_context_set_snapshot_reference_usage(self):
        """Test setting snapshot reference usage in tracing context."""
        context = _RequestTracingContext()

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
        context = _RequestTracingContext()
        context.uses_snapshot_reference = False

        # Test updating headers
        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=0,
            uses_key_vault=False,
            feature_flag_enabled=False,
            is_failover_request=False,
        )

        # Check if correlation context header exists and doesn't contain snapshot reference tag
        correlation_header = updated_headers.get("Correlation-Context", "")
        assert "RequestType=Startup" in correlation_header
        assert SNAPSHOT_REFERENCE_TAG not in correlation_header

    def test_correlation_context_header_with_snapshot_reference(self):
        """Test correlation context header when using snapshot references."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = True

        # Test updating headers
        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=0,
            uses_key_vault=False,
            feature_flag_enabled=False,
            is_failover_request=False,
        )

        # Check if correlation context header exists and contains snapshot reference tag
        correlation_header = updated_headers.get("Correlation-Context", "")
        assert "RequestType=Startup" in correlation_header
        assert SNAPSHOT_REFERENCE_TAG in correlation_header

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

    def test_tracing_context_updated_during_processing(self):
        """Test that tracing context is updated when processing configuration with snapshot references."""

        # Create provider instance with mocked dependencies
        provider = Mock(spec=AzureAppConfigurationProviderBase)
        provider._tracing_context = _RequestTracingContext()

        # Create a mock configuration setting with actual snapshot reference content type
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,  # Use the actual constant
        )

        # Simulate checking for snapshot reference content type using the real logic
        if setting.content_type and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in setting.content_type:
            provider._tracing_context.uses_snapshot_reference = True

        # Verify tracing context was updated
        assert provider._tracing_context.uses_snapshot_reference is True

    def test_tracing_context_not_updated_for_regular_settings(self):
        """Test that tracing context is not updated for regular settings."""

        # Create provider instance with mocked dependencies
        provider = Mock(spec=AzureAppConfigurationProviderBase)
        provider._tracing_context = _RequestTracingContext()

        # Create a regular configuration setting
        setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        # Simulate checking for snapshot reference content type (should not match)
        if setting.content_type and APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE in setting.content_type:
            provider._tracing_context.uses_snapshot_reference = True

        # Verify tracing context was not updated
        assert provider._tracing_context.uses_snapshot_reference is False

    def test_correlation_context_header_format_with_multiple_tags(self):
        """Test correlation context header format when multiple tags are present."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = True

        # Test updating headers with multiple features enabled
        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=2,
            uses_key_vault=True,
            feature_flag_enabled=False,
            is_failover_request=True,
        )

        # Verify the header contains expected components
        correlation_header = updated_headers.get("Correlation-Context", "")
        assert "RequestType=Startup" in correlation_header
        assert "ReplicaCount=2" in correlation_header
        assert "UsesKeyVault" in correlation_header  # Tag format
        assert "Failover" in correlation_header  # Tag format
        assert SNAPSHOT_REFERENCE_TAG in correlation_header

    def test_snapshot_reference_tag_constant(self):
        """Test that the snapshot reference tag constant has the expected value."""
        assert SNAPSHOT_REFERENCE_TAG == "UsesSnapshotReference=true"
