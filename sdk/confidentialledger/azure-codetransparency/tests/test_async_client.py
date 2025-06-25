# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from unittest.mock import Mock, AsyncMock

from azure.codetransparency.aio import AsyncCodeTransparencyClient
from azure.core.credentials_async import AsyncTokenCredential


class TestAsyncCodeTransparencyClient:
    """Test suite for AsyncCodeTransparencyClient."""

    def test_async_client_creation(self):
        """Test that the async client can be created with required parameters."""
        mock_credential = Mock(spec=AsyncTokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        client = AsyncCodeTransparencyClient(endpoint=endpoint, credential=mock_credential)
        
        assert client is not None
        assert client._config.endpoint == endpoint
        assert client._config.credential == mock_credential

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test that the async client works as a context manager."""
        mock_credential = Mock(spec=AsyncTokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        client = AsyncCodeTransparencyClient(endpoint=endpoint, credential=mock_credential)
        # Mock the pipeline methods
        client._client.__aenter__ = AsyncMock(return_value=client._client)
        client._client.__aexit__ = AsyncMock(return_value=None)
        
        async with client as ctx_client:
            assert ctx_client is not None

    @pytest.mark.asyncio
    async def test_async_client_close(self):
        """Test that the async client can be closed."""
        mock_credential = Mock(spec=AsyncTokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        client = AsyncCodeTransparencyClient(endpoint=endpoint, credential=mock_credential)
        # Mock the close method
        client._client.close = AsyncMock(return_value=None)
        
        await client.close()  # Should not raise an exception