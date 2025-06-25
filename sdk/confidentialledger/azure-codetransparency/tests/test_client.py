# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from unittest.mock import Mock

from azure.codetransparency import CodeTransparencyClient
from azure.core.credentials import TokenCredential


class TestCodeTransparencyClient:
    """Test suite for CodeTransparencyClient."""

    def test_client_creation(self):
        """Test that the client can be created with required parameters."""
        mock_credential = Mock(spec=TokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=mock_credential)
        
        assert client is not None
        assert client._config.endpoint == endpoint
        assert client._config.credential == mock_credential

    def test_client_context_manager(self):
        """Test that the client works as a context manager."""
        mock_credential = Mock(spec=TokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        with CodeTransparencyClient(endpoint=endpoint, credential=mock_credential) as client:
            assert client is not None

    def test_client_close(self):
        """Test that the client can be closed."""
        mock_credential = Mock(spec=TokenCredential)
        endpoint = "https://example.codetransparency.azure.com"
        
        client = CodeTransparencyClient(endpoint=endpoint, credential=mock_credential)
        client.close()  # Should not raise an exception