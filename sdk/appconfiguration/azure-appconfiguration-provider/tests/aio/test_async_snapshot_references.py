# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest.mock import Mock, AsyncMock, patch
from azure.appconfiguration import ConfigurationSetting, SnapshotComposition
from azure.appconfiguration.provider._snapshot_reference_parser import SnapshotReferenceParser
from azure.appconfiguration.provider._constants import SNAPSHOT_REF_CONTENT_TYPE
from azure.appconfiguration.provider.aio._async_client_manager import _AsyncConfigurationClientWrapper
from azure.core.exceptions import HttpResponseError


class TestResolveSnapshotReferenceAsync:
    """Async tests for the resolve_snapshot_reference method in _AsyncConfigurationClientWrapper."""

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_success_async(self):
        """Test successfully resolving a snapshot reference asynchronously."""
        # Create mock client
        mock_app_config_client = AsyncMock()
        wrapper = _AsyncConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock snapshot
        mock_snapshot = Mock()
        mock_snapshot.composition_type = SnapshotComposition.KEY
        mock_app_config_client.get_snapshot.return_value = mock_snapshot

        # Mock configuration settings from snapshot
        mock_settings = [
            ConfigurationSetting(key="key1", value="value1"),
            ConfigurationSetting(key="key2", value="value2"),
        ]

        with patch.object(wrapper, "load_configuration_settings", new_callable=AsyncMock, return_value=mock_settings):
            setting = ConfigurationSetting(
                key="SnapshotRef1",
                value='{"snapshot_name": "test-snapshot"}',
                content_type=SNAPSHOT_REF_CONTENT_TYPE,
            )

            result = await wrapper.resolve_snapshot_reference(setting)

            assert result == mock_settings
            mock_app_config_client.get_snapshot.assert_called_once_with("test-snapshot")

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_not_found_returns_empty_list_async(self):
        """Test that 404 error when resolving snapshot reference returns empty list asynchronously."""
        # Create mock client that raises 404
        mock_app_config_client = AsyncMock()
        wrapper = _AsyncConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        # Mock get_snapshot to raise 404
        http_error = HttpResponseError("Not Found")
        http_error.status_code = 404
        mock_app_config_client.get_snapshot.side_effect = http_error

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "non-existent-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        result = await wrapper.resolve_snapshot_reference(setting)

        assert result == []
        mock_app_config_client.get_snapshot.assert_called_once_with("non-existent-snapshot")

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_non_404_error_raises_async(self):
        """Test that non-404 HTTP errors are raised asynchronously."""
        # Create mock client that raises 500
        mock_app_config_client = AsyncMock()
        wrapper = _AsyncConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

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
            await wrapper.resolve_snapshot_reference(setting)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_invalid_composition_type_raises_async(self):
        """Test that invalid snapshot composition type raises ValueError asynchronously."""
        # Create mock client
        mock_app_config_client = AsyncMock()
        wrapper = _AsyncConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

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
            await wrapper.resolve_snapshot_reference(setting)

    @pytest.mark.asyncio
    async def test_resolve_snapshot_reference_invalid_content_type_raises_async(self):
        """Test that invalid content type raises ValueError asynchronously."""
        # Create mock client
        mock_app_config_client = AsyncMock()
        wrapper = _AsyncConfigurationClientWrapper("http://test.endpoint", mock_app_config_client)

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type="application/json",  # Wrong content type
        )

        with pytest.raises(ValueError, match="Setting is not a snapshot reference"):
            await wrapper.resolve_snapshot_reference(setting)
