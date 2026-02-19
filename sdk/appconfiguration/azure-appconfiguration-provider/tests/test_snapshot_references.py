# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, MagicMock
from azure.appconfiguration import ConfigurationSetting, SnapshotComposition
from azure.appconfiguration.provider._snapshot_reference_parser import SnapshotReferenceParser
from azure.appconfiguration.provider._constants import (
    SNAPSHOT_REF_CONTENT_TYPE,
)
from azure.appconfiguration.provider._client_manager import _ConfigurationClientWrapper
from azure.core.exceptions import HttpResponseError


class TestSnapshotReferenceParser:
    """Tests for the SnapshotReferenceParser class."""

    def test_parse_valid_snapshot_reference(self):
        """Test parsing a valid snapshot reference."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = SnapshotReferenceParser.parse(setting)

        assert isinstance(result, str)
        assert result == "test-snapshot"

    def test_parse_snapshot_reference_with_whitespace(self):
        """Test parsing a snapshot reference with whitespace in snapshot name."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "  test-snapshot  "}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = SnapshotReferenceParser.parse(setting)

        assert isinstance(result, str)
        assert result == "test-snapshot"  # Should be trimmed

    def test_parse_none_setting_raises_error(self):
        """Test that parsing None setting raises ValueError."""
        with pytest.raises(ValueError, match="Setting cannot be None"):
            SnapshotReferenceParser.parse(None)

    def test_parse_empty_value_raises_error(self):
        """Test that parsing empty value raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value="{}",
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*snapshot_name.*is required"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_whitespace_value_raises_error(self):
        """Test that parsing whitespace-only value raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value="   ",
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Value cannot be empty"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_invalid_json_raises_error(self):
        """Test that parsing invalid JSON raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value="{invalid json, missing quotes}",
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Invalid JSON format"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_non_object_json_raises_error(self):
        """Test that parsing non-object JSON raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='"just a string"',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*Expected JSON object"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_missing_snapshot_name_property_raises_error(self):
        """Test that missing snapshot_name property raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"other_property": "value"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*property is required"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_non_string_snapshot_name_raises_error(self):
        """Test that non-string snapshot_name property raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": 123}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*must be a string value"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_empty_snapshot_name_raises_error(self):
        """Test that empty snapshot_name raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": ""}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*cannot be empty or whitespace"):
            SnapshotReferenceParser.parse(setting)

    def test_parse_whitespace_snapshot_name_raises_error(self):
        """Test that whitespace-only snapshot_name raises ValueError."""
        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "   "}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Invalid snapshot reference format.*cannot be empty or whitespace"):
            SnapshotReferenceParser.parse(setting)


class TestResolveSnapshotReference:
    """Tests for the resolve_snapshot_reference method in _ConfigurationClientWrapper."""

    def test_resolve_snapshot_reference_success(self):
        """Test successfully resolving a snapshot reference."""
        # Create mock client
        mock_app_config_client = Mock()
        wrapper = _ConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock snapshot
        mock_snapshot = Mock()
        mock_snapshot.composition_type = SnapshotComposition.KEY
        mock_app_config_client.get_snapshot.return_value = mock_snapshot

        # Mock configuration settings from snapshot
        mock_settings = [
            ConfigurationSetting(key="key1", value="value1"),
            ConfigurationSetting(key="key2", value="value2"),
        ]

        with patch.object(wrapper, "load_configuration_settings", return_value=mock_settings):
            setting = ConfigurationSetting(
                key="SnapshotRef1",
                value='{"snapshot_name": "test-snapshot"}',
                content_type=SNAPSHOT_REF_CONTENT_TYPE,
            )

            result = wrapper.resolve_snapshot_reference(setting)

            assert result == mock_settings
            mock_app_config_client.get_snapshot.assert_called_once_with("test-snapshot")

    def test_resolve_snapshot_reference_not_found_returns_empty_list(self):
        """Test that 404 error when resolving snapshot reference returns empty list."""
        # Create mock client that raises 404
        mock_app_config_client = Mock()
        wrapper = _ConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock get_snapshot to raise 404
        http_error = HttpResponseError("Not Found")
        http_error.status_code = 404
        mock_app_config_client.get_snapshot.side_effect = http_error

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "non-existent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = wrapper.resolve_snapshot_reference(setting)

        assert result == []
        mock_app_config_client.get_snapshot.assert_called_once_with("non-existent-snapshot")

    def test_resolve_snapshot_reference_non_404_error_raises(self):
        """Test that non-404 HTTP errors are raised."""
        # Create mock client that raises 500
        mock_app_config_client = Mock()
        wrapper = _ConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock get_snapshot to raise 500 error
        http_error = HttpResponseError("Internal Server Error")
        http_error.status_code = 500
        mock_app_config_client.get_snapshot.side_effect = http_error

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(HttpResponseError) as exc_info:
            wrapper.resolve_snapshot_reference(setting)

        assert exc_info.value.status_code == 500

    def test_resolve_snapshot_reference_invalid_composition_type_raises(self):
        """Test that invalid snapshot composition type raises ValueError."""
        # Create mock client
        mock_app_config_client = Mock()
        wrapper = _ConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock snapshot with invalid composition type
        mock_snapshot = Mock()
        mock_snapshot.composition_type = "invalid"  # Not SnapshotComposition.KEY
        mock_app_config_client.get_snapshot.return_value = mock_snapshot

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with pytest.raises(ValueError, match="Composition type for 'test-snapshot' must be 'key'."):
            wrapper.resolve_snapshot_reference(setting)

    def test_resolve_snapshot_reference_invalid_content_type_raises(self):
        """Test that invalid content type raises ValueError."""
        # Create mock client
        mock_app_config_client = Mock()
        wrapper = _ConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type="application/json",  # Wrong content type
        )

        with pytest.raises(ValueError, match="Setting is not a snapshot reference"):
            wrapper.resolve_snapshot_reference(setting)
