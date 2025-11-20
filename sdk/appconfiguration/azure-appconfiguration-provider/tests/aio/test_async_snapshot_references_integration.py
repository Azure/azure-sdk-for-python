# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, AsyncMock
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider.aio._async_client_manager import AsyncConfigurationClientManager
from azure.appconfiguration.provider._constants import SNAPSHOT_REF_CONTENT_TYPE
from azure.core.exceptions import ResourceNotFoundError, AzureError
from azure.identity.aio import DefaultAzureCredential


class TestAsyncClientManagerSnapshotReferences:
    """Integration tests for snapshot references in the async client manager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Azure App Configuration async client."""
        client = AsyncMock()

        async def mock_list_settings(*args, **kwargs):
            # Return an async iterator
            for item in []:
                yield item

        client.list_configuration_settings = mock_list_settings
        return client

    @pytest.fixture
    def client_manager(self, mock_client):
        """Create an async client manager with mocked client."""
        with patch("azure.appconfiguration.aio.AzureAppConfigurationClient", return_value=mock_client):
            return AsyncConfigurationClientManager(
                connection_string=None,
                endpoint="https://test.azconfig.io",
                credential=DefaultAzureCredential(),
                user_agent="test-user-agent",
                retry_total=3,
                retry_backoff_max=60,
                replica_discovery_enabled=False,
                min_backoff_sec=30,
                max_backoff_sec=600,
                load_balancing_enabled=False,
            )

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_success(self, client_manager, mock_client):
        """Test successfully resolving a snapshot reference."""
        # Setup snapshot reference setting
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Setup snapshot data
        snapshot_settings = [
            ConfigurationSetting(key="App:Setting1", value="SnapshotValue1"),
            ConfigurationSetting(key="App:Setting2", value="SnapshotValue2"),
        ]

        # Mock the load_configuration_settings method to return snapshot data
        with patch.object(
            client_manager._original_client, "load_configuration_settings", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = snapshot_settings

            # Test resolving the snapshot reference
            result = await client_manager._original_client.resolve_snapshot_reference(snapshot_ref)

            assert result == {"App:Setting1": snapshot_settings[0], "App:Setting2": snapshot_settings[1]}
            mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_snapshot_not_found(self, client_manager, mock_client):
        """Test resolving a snapshot reference when snapshot doesn't exist."""
        # Setup snapshot reference setting
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "nonexistent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        with patch.object(
            client_manager._original_client, "load_configuration_settings", new_callable=AsyncMock
        ) as mock_load:
            mock_load.side_effect = AzureError("Snapshot not found")

            # Test resolving the snapshot reference
            with pytest.raises(ValueError, match="Failed to resolve snapshot reference.*Azure service error occurred"):
                await client_manager._original_client.resolve_snapshot_reference(snapshot_ref)

    @pytest.mark.asyncio
    async def test_load_snapshot_data_success(self, client_manager, mock_client):
        """Test successfully loading snapshot data."""
        # Setup snapshot data
        snapshot_settings = [
            ConfigurationSetting(key="App:Setting1", value="SnapshotValue1"),
            ConfigurationSetting(key="App:Setting2", value="SnapshotValue2"),
        ]

        # Setup mock responses
        async def mock_list_settings(*args, **kwargs):
            for setting in snapshot_settings:
                yield setting

        mock_client.list_configuration_settings = mock_list_settings
        mock_client.get_snapshot = AsyncMock(return_value=Mock(composition_type="key"))

        # Test loading snapshot data using load_configuration_settings
        selector = SettingSelector(snapshot_name="test-snapshot")
        result = await client_manager._original_client.load_configuration_settings([selector])

        assert result == snapshot_settings


class TestAzureAppConfigurationProviderAsyncSnapshotReferences:
    """Integration tests for snapshot references in the async provider."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Azure App Configuration async client."""
        client = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_provider_processes_snapshot_reference(self, mock_client):
        """Test that the async provider correctly processes snapshot references during configuration loading."""
        # Setup configuration settings including a snapshot reference
        regular_setting = ConfigurationSetting(key="App:RegularSetting", value="RegularValue")
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Setup snapshot data
        snapshot_settings = [
            ConfigurationSetting(key="App:SnapshotSetting1", value="SnapshotValue1"),
            ConfigurationSetting(key="App:SnapshotSetting2", value="SnapshotValue2"),
        ]

        # Configure mock to return different data for different calls
        async def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                for setting in snapshot_settings:
                    yield setting
            else:
                for setting in [regular_setting, snapshot_ref]:
                    yield setting

        mock_client.list_configuration_settings = mock_list_settings

        # Test with the provider
        with patch("azure.appconfiguration.aio.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider.aio import load

            provider = await load(
                endpoint="https://test.azconfig.io",
                credential=DefaultAzureCredential(),
            )

            # Verify that all settings are present in the provider
            assert "App:RegularSetting" in provider
            assert "App:SnapshotSetting1" in provider
            assert "App:SnapshotSetting2" in provider
            assert provider["App:RegularSetting"] == "RegularValue"
            assert provider["App:SnapshotSetting1"] == "SnapshotValue1"
            assert provider["App:SnapshotSetting2"] == "SnapshotValue2"

            # The snapshot reference itself should not be in the configuration
            assert "SnapshotRef1" not in provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_provider_handles_snapshot_reference_error(self, mock_client):
        """Test that the async provider handles snapshot reference errors gracefully."""
        # Setup configuration with a snapshot reference that will fail
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "nonexistent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        async def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                raise ResourceNotFoundError("Snapshot not found")
            else:
                for setting in [snapshot_ref]:
                    yield setting

        mock_client.list_configuration_settings = mock_list_settings

        # Test that provider creation fails with appropriate error
        with patch("azure.appconfiguration.aio.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider.aio import load

            with pytest.raises(ValueError, match="Failed to resolve snapshot reference.*Azure service error occurred"):
                provider = await load(
                    endpoint="https://test.azconfig.io",
                    credential=DefaultAzureCredential(),
                )

    @pytest.mark.asyncio
    async def test_provider_with_selectors_and_snapshot_references(self, mock_client):
        """Test async provider behavior with selectors when processing snapshot references."""
        # Setup configuration settings
        regular_setting = ConfigurationSetting(key="App:RegularSetting", value="RegularValue")
        other_setting = ConfigurationSetting(key="Other:Setting", value="OtherValue")
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Setup snapshot data (contains both App:* and Other:* keys)
        snapshot_settings = [
            ConfigurationSetting(key="App:SnapshotSetting1", value="SnapshotValue1"),
            ConfigurationSetting(key="Other:SnapshotSetting1", value="OtherSnapshotValue1"),
        ]

        async def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                for setting in snapshot_settings:
                    yield setting
            else:
                for setting in [regular_setting, other_setting, snapshot_ref]:
                    yield setting

        mock_client.list_configuration_settings = mock_list_settings

        # Test with selectors that only include App:* keys
        with patch("azure.appconfiguration.aio.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider.aio import load

            provider = await load(
                endpoint="https://test.azconfig.io",
                credential=DefaultAzureCredential(),
                selects=[SettingSelector(key_filter="App:*")],
            )

            # Should include regular App:* setting and snapshot App:* setting
            assert "App:RegularSetting" in provider
            assert "App:SnapshotSetting1" in provider

            # Should not include Other:* settings (filtered out by selector)
            assert "Other:Setting" not in provider
            assert "Other:SnapshotSetting1" not in provider

            # Snapshot reference itself should not be present
            assert "SnapshotRef1" not in provider

            await provider.close()

    @pytest.mark.asyncio
    async def test_provider_recursive_snapshot_processing(self, mock_client):
        """Test that async provider correctly handles recursive snapshot reference processing."""
        # Setup configuration settings with feature flags
        feature_flag = ConfigurationSetting(
            key=".appconfig.featureflag/TestFlag",
            value='{"enabled": true, "conditions": {"client_filters": []}}',
            content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
        )

        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Setup snapshot data that includes both regular settings and feature flags
        snapshot_settings = [
            ConfigurationSetting(key="App:SnapshotSetting1", value="SnapshotValue1"),
            ConfigurationSetting(
                key=".appconfig.featureflag/SnapshotFlag",
                value='{"enabled": false, "conditions": {"client_filters": []}}',
                content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            ),
        ]

        async def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                for setting in snapshot_settings:
                    yield setting
            else:
                # Filter based on key_filter
                key_filter = kwargs.get("key_filter", "")
                if key_filter.startswith(".appconfig.featureflag/"):
                    yield feature_flag
                else:
                    yield snapshot_ref

        mock_client.list_configuration_settings = mock_list_settings

        # Test with feature flags enabled
        with patch("azure.appconfiguration.aio.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider.aio import load

            provider = await load(
                endpoint="https://test.azconfig.io",
                credential=DefaultAzureCredential(),
                feature_flag_enabled=True,
            )

            # Should include regular snapshot setting
            assert "App:SnapshotSetting1" in provider
            assert provider["App:SnapshotSetting1"] == "SnapshotValue1"

            # Should include feature flags from both regular config and snapshot
            assert "feature_management" in provider
            feature_flags = provider["feature_management"]["feature_flags"]
            flag_names = [flag["id"] for flag in feature_flags]
            assert "TestFlag" in flag_names
            assert "SnapshotFlag" in flag_names

            await provider.close()
