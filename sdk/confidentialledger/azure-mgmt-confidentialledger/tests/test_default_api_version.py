# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.confidentialledger import ConfidentialLedger
from azure.mgmt.confidentialledger.aio import ConfidentialLedger as AsyncConfidentialLedger
from unittest.mock import Mock


class TestDefaultApiVersion:
    """Test that the default API version is correctly set."""

    def test_sync_default_api_version(self):
        """Test that synchronous client uses the correct default API version."""
        # Create a mock credential
        mock_credential = Mock()
        mock_credential.get_token = Mock(return_value=Mock(token="fake_token"))
        
        # Create client without specifying api_version
        client = ConfidentialLedger(
            credential=mock_credential,
            subscription_id="00000000-0000-0000-0000-000000000000"
        )
        
        # Verify the default api_version is set correctly
        assert client._config.api_version == "2025-06-10-preview"

    def test_sync_custom_api_version(self):
        """Test that synchronous client can use a custom API version."""
        # Create a mock credential
        mock_credential = Mock()
        mock_credential.get_token = Mock(return_value=Mock(token="fake_token"))
        
        # Create client with a custom api_version
        client = ConfidentialLedger(
            credential=mock_credential,
            subscription_id="00000000-0000-0000-0000-000000000000",
            api_version="2024-09-19-preview"
        )
        
        # Verify the custom api_version is used
        assert client._config.api_version == "2024-09-19-preview"

    @pytest.mark.asyncio
    async def test_async_default_api_version(self):
        """Test that asynchronous client uses the correct default API version."""
        # Create a mock credential
        mock_credential = Mock()
        mock_credential.get_token = Mock(return_value=Mock(token="fake_token"))
        
        # Create client without specifying api_version
        client = AsyncConfidentialLedger(
            credential=mock_credential,
            subscription_id="00000000-0000-0000-0000-000000000000"
        )
        
        # Verify the default api_version is set correctly
        assert client._config.api_version == "2025-06-10-preview"
        
        # Clean up
        await client.close()

    @pytest.mark.asyncio
    async def test_async_custom_api_version(self):
        """Test that asynchronous client can use a custom API version."""
        # Create a mock credential
        mock_credential = Mock()
        mock_credential.get_token = Mock(return_value=Mock(token="fake_token"))
        
        # Create client with a custom api_version
        client = AsyncConfidentialLedger(
            credential=mock_credential,
            subscription_id="00000000-0000-0000-0000-000000000000",
            api_version="2024-09-19-preview"
        )
        
        # Verify the custom api_version is used
        assert client._config.api_version == "2024-09-19-preview"
        
        # Clean up
        await client.close()
