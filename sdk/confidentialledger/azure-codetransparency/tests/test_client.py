# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import os
import pytest
from unittest.mock import Mock
from azure.codetransparency import CodeTransparencyClient


class TestCodeTransparencyClient:
    """Test suite for CodeTransparencyClient."""

    def test_client_creation(self):
        """Test that the client can be created successfully."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=credential)
        
        assert client is not None
        assert hasattr(client, '_config')
        assert hasattr(client, '_client')

    def test_client_context_manager(self):
        """Test that the client works as a context manager."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        with CodeTransparencyClient(endpoint=endpoint, credential=credential) as client:
            assert client is not None

    def test_client_close(self):
        """Test that the client can be closed properly."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=credential)
        client.close()  # Should not raise an exception

    def test_client_with_api_version(self):
        """Test client creation with custom API version."""
        endpoint = "https://test.confidentialledger.azure.com/"
        credential = Mock()  # Mock credential for testing
        api_version = "2025-01-31-preview"
        
        client = CodeTransparencyClient(
            endpoint=endpoint, 
            credential=credential, 
            api_version=api_version
        )
        
        assert client._config.api_version == api_version

    def test_client_missing_endpoint(self):
        """Test that client creation fails with missing endpoint."""
        credential = Mock()  # Mock credential for testing
        
        with pytest.raises(ValueError, match="Parameter 'endpoint' must not be None"):
            CodeTransparencyClient(endpoint=None, credential=credential)

    def test_client_missing_credential(self):
        """Test that client creation fails with missing credential."""
        endpoint = "https://test.confidentialledger.azure.com/"
        
        with pytest.raises(ValueError, match="Parameter 'credential' must not be None"):
            CodeTransparencyClient(endpoint=endpoint, credential=None)