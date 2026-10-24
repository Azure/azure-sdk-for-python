# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import pytest
import asyncio
from unittest.mock import Mock
from azure.codetransparency.aio import CodeTransparencyClient


class TestAsyncCodeTransparencyClient:
    """Test suite for async CodeTransparencyClient."""

    @pytest.mark.asyncio
    async def test_async_client_creation(self):
        """Test that the async client can be created successfully."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=credential)
        
        assert client is not None
        assert hasattr(client, '_config')
        assert hasattr(client, '_client')
        
        await client.close()

    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """Test that the async client works as a context manager."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        async with CodeTransparencyClient(endpoint=endpoint, credential=credential) as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_async_client_close(self):
        """Test that the async client can be closed properly."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=credential)
        await client.close()  # Should not raise an exception

    @pytest.mark.asyncio
    async def test_async_client_with_api_version(self):
        """Test async client creation with custom API version."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        api_version = "2025-01-31-preview"
        
        client = CodeTransparencyClient(
            endpoint=endpoint, 
            credential=credential, 
            api_version=api_version
        )
        
        assert client._config.api_version == api_version
        await client.close()

    def test_async_client_missing_endpoint(self):
        """Test that async client creation fails with missing endpoint."""
        credential = Mock()  # Mock credential for testing
        
        with pytest.raises(ValueError, match="Parameter 'endpoint' must not be None"):
            CodeTransparencyClient(endpoint=None, credential=credential)

    def test_async_client_missing_credential(self):
        """Test that async client creation fails with missing credential."""
        endpoint = "https://test.confidentialledger.azure.com/"
        
        with pytest.raises(ValueError, match="Parameter 'credential' must not be None"):
            CodeTransparencyClient(endpoint=endpoint, credential=None)