# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import pytest
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy, is_live
from preparers import app_config_decorator
from testcase import AppConfigTestCase
from azure.appconfiguration import (
    ConfigurationSetting,
    ConfigurationSettingsFilter,
    SnapshotComposition,
    SnapshotStatus,
)
from azure.appconfiguration.provider._models import SettingSelector
from azure.appconfiguration.provider._constants import NULL_CHAR
from azure.appconfiguration.provider import load, WatchKey


class TestSnapshotSupport:
    """Tests for snapshot functionality in SettingSelector."""

    def test_setting_selector_with_snapshot_name(self):
        """Test SettingSelector with snapshot_name parameter."""
        selector = SettingSelector(snapshot_name="my-snapshot")
        assert selector.snapshot_name == "my-snapshot"
        assert selector.key_filter is None
        assert selector.label_filter == NULL_CHAR
        assert selector.tag_filters is None

    def test_setting_selector_snapshot_name_with_key_filter_raises_error(self):
        """Test that SettingSelector raises ValueError when both snapshot_name and key_filter are provided."""
        with pytest.raises(
            ValueError,
            match=r"Cannot specify both snapshot_name and key_filter\. "
            r"When using snapshots, all other filtering parameters are ignored\.",
        ):
            SettingSelector(snapshot_name="my-snapshot", key_filter="*")

    def test_setting_selector_snapshot_name_with_label_filter_raises_error(self):
        """Test that SettingSelector raises ValueError when both snapshot_name and label_filter are provided."""
        with pytest.raises(
            ValueError,
            match=r"Cannot specify both snapshot_name and label_filter\. "
            r"When using snapshots, all other filtering parameters are ignored\.",
        ):
            SettingSelector(snapshot_name="my-snapshot", label_filter="prod")

    def test_setting_selector_snapshot_name_with_tag_filters_raises_error(self):
        """Test that SettingSelector raises ValueError when both snapshot_name and tag_filters are provided."""
        with pytest.raises(
            ValueError,
            match=r"Cannot specify both snapshot_name and tag_filters\. "
            r"When using snapshots, all other filtering parameters are ignored\.",
        ):
            SettingSelector(snapshot_name="my-snapshot", tag_filters=["env=prod"])

    def test_setting_selector_requires_key_filter_or_snapshot_name(self):
        """Test that SettingSelector requires either key_filter or snapshot_name."""
        with pytest.raises(ValueError, match=r"Either key_filter or snapshot_name must be specified\."):
            SettingSelector()

    def test_setting_selector_valid_combinations(self):
        """Test valid combinations of SettingSelector parameters."""
        # Valid: key_filter only
        selector = SettingSelector(key_filter="*")
        assert selector.key_filter == "*"
        assert selector.snapshot_name is None

        # Valid: snapshot_name only
        selector = SettingSelector(snapshot_name="my-snapshot")
        assert selector.snapshot_name == "my-snapshot"
        assert selector.key_filter is None

        # Valid: key_filter with other filters (no snapshot_name)
        selector = SettingSelector(key_filter="*", label_filter="prod", tag_filters=["env=prod"])
        assert selector.key_filter == "*"
        assert selector.label_filter == "prod"
        assert selector.tag_filters == ["env=prod"]
        assert selector.snapshot_name is None

    def test_feature_flag_selectors_with_snapshot_raises_error(self):
        """Test that feature_flag_selectors with snapshot_name raises ValueError during validation."""
        with pytest.raises(
            ValueError,
            match=r"snapshot_name cannot be used with feature_flag_selectors\. "
            r"Use snapshot_name with regular selects instead to load feature flags from snapshots\.",
        ):
            load(
                connection_string="Endpoint=test;Id=test;Secret=test",
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(snapshot_name="my-snapshot")],
            )


class TestSnapshotProviderIntegration(AppConfigTestCase):
    """Integration tests for snapshot functionality with recorded tests."""

    def test_setting_selector_multiple_combinations(self):
        """Test using multiple selectors with mix of snapshot and regular selectors."""
        # This should be valid - mixing snapshot and regular selectors
        selectors = [
            SettingSelector(snapshot_name="config-snapshot"),  # Load from snapshot
            SettingSelector(key_filter="runtime.*"),  # Load runtime configs from current state
        ]

        # Validate each selector individually
        assert selectors[0].snapshot_name == "config-snapshot"
        assert selectors[0].key_filter is None

        assert selectors[1].key_filter == "runtime.*"
        assert selectors[1].snapshot_name is None

    def test_snapshot_with_different_names(self):
        """Test snapshot selectors with different snapshot names."""
        # Different snapshot names should be valid
        snapshot1 = SettingSelector(snapshot_name="prod-config-v1.0")
        snapshot2 = SettingSelector(snapshot_name="staging-config-v2.1")

        assert snapshot1.snapshot_name == "prod-config-v1.0"
        assert snapshot2.snapshot_name == "staging-config-v2.1"

        # Both should have no other filters
        for selector in [snapshot1, snapshot2]:
            assert selector.key_filter is None
            assert selector.label_filter == NULL_CHAR
            assert selector.tag_filters is None

    @app_config_decorator
    @recorded_by_proxy
    def test_load_provider_with_snapshot_not_found(self, appconfiguration_connection_string):
        """Test loading provider with a non-existent snapshot returns error."""
        # Try to load from a non-existent snapshot
        with pytest.raises(ResourceNotFoundError):
            self.create_client(
                connection_string=appconfiguration_connection_string,
                selects=[SettingSelector(snapshot_name="non-existent-snapshot")],
            )

    @app_config_decorator
    @recorded_by_proxy
    def test_load_provider_with_regular_selectors(self, appconfiguration_connection_string):
        """Test loading provider with regular selectors works (baseline test)."""
        # This should work - regular selector loading
        provider = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=[SettingSelector(key_filter="message")],  # Regular selector
        )

        # Verify we can access the configuration (message is set up by setup_configs)
        assert "message" in provider

    @app_config_decorator
    @recorded_by_proxy
    def test_snapshot_selector_parameter_validation_in_provider(self, appconfiguration_connection_string):
        """Test that snapshot selector parameter validation works when loading provider."""
        # Test that feature flag selectors with snapshots are rejected
        with pytest.raises(ValueError, match="snapshot_name cannot be used with feature_flag_selectors"):
            self.create_client(
                connection_string=appconfiguration_connection_string,
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(snapshot_name="test-snapshot")],
            )

    @pytest.mark.live_test_only  # Needed to fix an azure core dependency compatibility issue
    @app_config_decorator
    @recorded_by_proxy
    def test_create_snapshot_and_load_provider(self, appconfiguration_connection_string, **kwargs):
        """Test creating a snapshot and loading provider from it."""
        # Create SDK client for setup
        sdk_client = self.create_sdk_client(appconfiguration_connection_string)

        # Create unique test configuration settings for the snapshot
        test_settings = [
            ConfigurationSetting(key="snapshot_test_key1", value="snapshot_test_value1", label=NULL_CHAR),
            ConfigurationSetting(key="snapshot_test_key2", value="snapshot_test_value2", label=NULL_CHAR),
            ConfigurationSetting(
                key="snapshot_test_json",
                value='{"nested": "snapshot_value"}',
                label=NULL_CHAR,
                content_type="application/json",
            ),
            ConfigurationSetting(key="refresh_test_key", value="original_refresh_value", label=NULL_CHAR),
        ]

        # Set the configuration settings
        for setting in test_settings:
            sdk_client.set_configuration_setting(setting)

        variables = kwargs.pop("variables", {})
        dynamic_snapshot_name_postfix = variables.setdefault("dynamic_snapshot_name_postfix", str(int(time.time())))

        # Create a unique snapshot name with timestamp to avoid conflicts
        snapshot_name = f"test-snapshot-{dynamic_snapshot_name_postfix}"

        try:
            # Create the snapshot
            snapshot = sdk_client.begin_create_snapshot(
                name=snapshot_name,
                filters=[ConfigurationSettingsFilter(key="snapshot_test_*")],  # Include all our test keys
                composition_type=SnapshotComposition.KEY,
                retention_period=3600,  # Min valid value is 1 hour
            ).result()

            # Verify snapshot was created successfully
            if is_live():
                assert snapshot.name == snapshot_name
            else:
                assert snapshot.name == "Sanitized"
            assert snapshot.status == SnapshotStatus.READY
            assert snapshot.composition_type == SnapshotComposition.KEY

            # Load provider using the snapshot with refresh enabled
            provider = self.create_client(
                connection_string=appconfiguration_connection_string,
                selects=[
                    SettingSelector(snapshot_name=snapshot_name),  # Snapshot data
                    SettingSelector(key_filter="refresh_test_key"),  # Non-snapshot key for refresh testing
                ],
                refresh_on=[WatchKey("refresh_test_key")],  # Watch non-snapshot key for refresh
                refresh_interval=1,  # Short refresh interval for testing
            )

            # Verify all snapshot settings are loaded
            assert provider["snapshot_test_key1"] == "snapshot_test_value1"
            assert provider["snapshot_test_key2"] == "snapshot_test_value2"
            assert provider["snapshot_test_json"]["nested"] == "snapshot_value"
            assert provider["refresh_test_key"] == "original_refresh_value"

            # Verify that snapshot settings and refresh key are loaded
            snapshot_keys = [key for key in provider.keys() if key.startswith("snapshot_test_")]
            assert len(snapshot_keys) == 3

            # Test snapshot immutability: modify the original settings
            modified_settings = [
                ConfigurationSetting(
                    key="snapshot_test_key1", value="MODIFIED_VALUE1", label=NULL_CHAR  # Changed value
                ),
                ConfigurationSetting(
                    key="snapshot_test_key2", value="MODIFIED_VALUE2", label=NULL_CHAR  # Changed value
                ),
                ConfigurationSetting(
                    key="snapshot_test_json",
                    value='{"nested": "MODIFIED_VALUE"}',  # Changed nested value
                    label=NULL_CHAR,
                    content_type="application/json",
                ),
                ConfigurationSetting(
                    key="refresh_test_key",
                    value="updated_refresh_value",  # Changed value to trigger refresh
                    label=NULL_CHAR,
                ),
            ]

            # Update the original settings with new values
            for setting in modified_settings:
                sdk_client.set_configuration_setting(setting)

            # Add a completely new key after initial load
            new_key = ConfigurationSetting(key="new_key_added_after_load", value="new_value", label=NULL_CHAR)
            sdk_client.set_configuration_setting(new_key)

            # Wait for refresh interval to pass
            time.sleep(1)

            # Refresh the existing provider (snapshots should remain immutable, but non-snapshot keys should update)
            provider.refresh()

            # Verify the snapshot still contains the original values after refresh (immutability)
            assert provider["snapshot_test_key1"] == "snapshot_test_value1"  # Original value
            assert provider["snapshot_test_key2"] == "snapshot_test_value2"  # Original value
            assert provider["snapshot_test_json"]["nested"] == "snapshot_value"  # Original value

            # Verify the non-snapshot key was updated during refresh
            assert provider["refresh_test_key"] == "updated_refresh_value"  # Updated value

            # Verify new keys are NOT added during refresh (only watched keys trigger full reload)
            assert "new_key_added_after_load" not in provider  # New key should not be loaded

            # Verify that loading without snapshot gets the modified values
            provider_current = self.create_client(
                connection_string=appconfiguration_connection_string,
                selects=[SettingSelector(key_filter="snapshot_test_*")],
            )

            # Current values should be the modified ones
            assert provider_current["snapshot_test_key1"] == "MODIFIED_VALUE1"  # Modified value
            assert provider_current["snapshot_test_key2"] == "MODIFIED_VALUE2"  # Modified value
            assert provider_current["snapshot_test_json"]["nested"] == "MODIFIED_VALUE"  # Modified value

        finally:
            # Clean up: delete the snapshot and test settings
            try:
                # Archive the snapshot (delete is not supported, but archive effectively removes it)
                sdk_client.archive_snapshot(snapshot_name)
            except Exception:
                pass

            # Clean up test settings
            for setting in test_settings:
                try:
                    sdk_client.delete_configuration_setting(key=setting.key, label=setting.label)
                except Exception:
                    pass

            # Clean up additional test keys
            try:
                sdk_client.delete_configuration_setting(key="new_key_added_after_load", label=NULL_CHAR)
            except Exception:
                pass
        return variables
