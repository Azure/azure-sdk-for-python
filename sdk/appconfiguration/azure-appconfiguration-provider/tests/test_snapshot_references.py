# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider._snapshot_reference_parser import SnapshotReferenceParser
from azure.appconfiguration.provider._constants import (
    APP_CONFIG_SNAPSHOT_REF_MIME_PROFILE,
    SNAPSHOT_REF_CONTENT_TYPE,
    SNAPSHOT_NAME_FIELD,
)


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
