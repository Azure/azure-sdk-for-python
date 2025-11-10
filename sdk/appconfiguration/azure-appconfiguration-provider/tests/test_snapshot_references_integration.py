# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, patch, AsyncMock
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider._client_manager import _ClientManager
from azure.appconfiguration.provider._constants import SNAPSHOT_REF_CONTENT_TYPE
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential


class TestClientManagerSnapshotReferences:
    """Integration tests for snapshot references in the client manager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Azure App Configuration client."""
        client = Mock()
        client.list_configuration_settings = Mock(return_value=[])
        return client

    @pytest.fixture
    def client_manager(self, mock_client):
        """Create a client manager with mocked client."""
        with patch("azure.appconfiguration.AzureAppConfigurationClient", return_value=mock_client):
            return _ClientManager("https://test.azconfig.io", DefaultAzureCredential(), "test-user-agent")

    def test_resolve_snapshot_reference_success(self, client_manager, mock_client):
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

        mock_client.list_configuration_settings.return_value = snapshot_settings

        # Test resolving the snapshot reference
        result = client_manager.resolve_snapshot_reference(snapshot_ref)

        assert result == snapshot_settings
        mock_client.list_configuration_settings.assert_called_once_with(snapshot_name="test-snapshot")

    def test_resolve_snapshot_reference_snapshot_not_found(self, client_manager, mock_client):
        """Test resolving a snapshot reference when snapshot doesn't exist."""
        # Setup snapshot reference setting
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "nonexistent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Setup client to raise ResourceNotFoundError
        mock_client.list_configuration_settings.side_effect = ResourceNotFoundError("Snapshot not found")

        # Test resolving the snapshot reference
        with pytest.raises(
            ValueError, match="Failed to resolve snapshot reference.*Snapshot 'nonexistent-snapshot' not found"
        ):
            client_manager.resolve_snapshot_reference(snapshot_ref)

    def test_load_snapshot_data_success(self, client_manager, mock_client):
        """Test successfully loading snapshot data."""
        # Setup snapshot data
        snapshot_settings = [
            ConfigurationSetting(key="App:Setting1", value="SnapshotValue1"),
            ConfigurationSetting(key="App:Setting2", value="SnapshotValue2"),
        ]

        mock_client.list_configuration_settings.return_value = snapshot_settings
        mock_client.get_snapshot.return_value = Mock(composition_type="key")

        # Test loading snapshot data using load_configuration_settings
        from azure.appconfiguration.provider import SettingSelector

        selector = SettingSelector(snapshot_name="test-snapshot")
        result = client_manager.load_configuration_settings([selector])

        assert result == snapshot_settings
        mock_client.list_configuration_settings.assert_called_once_with(snapshot_name="test-snapshot")


class TestAzureAppConfigurationProviderSnapshotReferences:
    """Integration tests for snapshot references in the provider."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Azure App Configuration client."""
        client = Mock()
        client.list_configuration_settings = Mock(return_value=[])
        return client

    def test_provider_processes_snapshot_reference(self, mock_client):
        """Test that the provider correctly processes snapshot references during configuration loading."""
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
        def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                return snapshot_settings
            else:
                return [regular_setting, snapshot_ref]

        mock_client.list_configuration_settings.side_effect = mock_list_settings

        # Test with the provider
        with patch("azure.appconfiguration.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider import AzureAppConfigurationProvider

            provider = AzureAppConfigurationProvider.load(
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

    def test_provider_handles_snapshot_reference_error(self, mock_client):
        """Test that the provider handles snapshot reference errors gracefully."""
        # Setup configuration with a snapshot reference that will fail
        snapshot_ref = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "nonexistent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                raise ResourceNotFoundError("Snapshot not found")
            else:
                return [snapshot_ref]

        mock_client.list_configuration_settings.side_effect = mock_list_settings

        # Test that provider creation fails with appropriate error
        with patch("azure.appconfiguration.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider import AzureAppConfigurationProvider

            with pytest.raises(
                ValueError, match="Failed to resolve snapshot reference.*Snapshot 'nonexistent-snapshot' not found"
            ):
                AzureAppConfigurationProvider.load(
                    endpoint="https://test.azconfig.io",
                    credential=DefaultAzureCredential(),
                )

    def test_provider_with_selectors_and_snapshot_references(self, mock_client):
        """Test provider behavior with selectors when processing snapshot references."""
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

        def mock_list_settings(*args, **kwargs):
            if "snapshot_name" in kwargs:
                return snapshot_settings
            else:
                return [regular_setting, other_setting, snapshot_ref]

        mock_client.list_configuration_settings.side_effect = mock_list_settings

        # Test with selectors that only include App:* keys
        with patch("azure.appconfiguration.AzureAppConfigurationClient", return_value=mock_client):
            from azure.appconfiguration.provider import AzureAppConfigurationProvider

            provider = AzureAppConfigurationProvider.load(
                endpoint="https://test.azconfig.io",
                credential=DefaultAzureCredential(),
                selectors=[SettingSelector(key_filter="App:*")],
            )

            # Should include regular App:* setting and snapshot App:* setting
            assert "App:RegularSetting" in provider
            assert "App:SnapshotSetting1" in provider

            # Should not include Other:* settings (filtered out by selector)
            assert "Other:Setting" not in provider
            assert "Other:SnapshotSetting1" not in provider

            # Snapshot reference itself should not be present
            assert "SnapshotRef1" not in provider
