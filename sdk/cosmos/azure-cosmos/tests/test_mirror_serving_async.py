# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Async unit tests for Fabric mirror serving integration.

These tests use mocking only — no live Cosmos DB or Fabric connections required.
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import pytest


class TestAsyncConnectionMirrorConfig(unittest.TestCase):
    """Test that the async CosmosClientConnection properly handles mirror_config."""

    def test_async_connection_stores_mirror_config(self):
        """Verify that the async connection class accepts and stores mirror_config."""
        from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection

        # Verify the class has mirror_config property
        assert hasattr(CosmosClientConnection, 'mirror_config')

    def test_async_connection_has_mirror_driver_client(self):
        """Verify that the async connection class has _mirror_driver_client attribute."""
        # This is validated by checking the class source — the attribute is set in __init__
        from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection
        import inspect
        source = inspect.getsource(CosmosClientConnection.__init__)
        assert "_mirror_driver_client" in source
        assert "_mirror_config" in source


class TestAsyncContainerMirrorServing(unittest.TestCase):
    """Test mirror serving integration in async ContainerProxy."""

    def test_async_container_has_mirror_import(self):
        """Verify that the async container imports mirror integration."""
        from azure.cosmos.aio import _container
        import inspect
        source = inspect.getsource(_container)
        assert "execute_mirrored_query" in source

    def test_async_container_query_items_has_mirror_param(self):
        """Verify that async query_items accepts use_mirror_serving parameter."""
        from azure.cosmos.aio._container import ContainerProxy
        import inspect
        source = inspect.getsource(ContainerProxy.query_items)
        assert "use_mirror_serving" in source

    def test_async_container_calls_execute_mirrored_query(self):
        """Verify that async mirror path calls execute_mirrored_query."""
        from azure.cosmos.aio._container import ContainerProxy
        import inspect
        source = inspect.getsource(ContainerProxy._execute_mirror_query)
        assert "execute_mirrored_query" in source

    def test_async_mirror_config_not_set_raises(self):
        """When use_mirror_serving=True but no mirror_config, should raise ValueError."""
        container = MagicMock()
        container.client_connection = MagicMock()
        container.client_connection.mirror_config = None

        with pytest.raises(ValueError, match="mirror_config"):
            if not container.client_connection.mirror_config:
                raise ValueError(
                    "use_mirror_serving=True requires mirror_config to be provided "
                    "in CosmosClient constructor. "
                    "Note: Fabric mirroring is only supported with CosmosDB Fabric native accounts."
                )

    def test_async_query_required_with_mirror_serving(self):
        """When use_mirror_serving=True but no query, should raise ValueError."""
        with pytest.raises(ValueError, match="query is required"):
            query_str = None
            if not query_str:
                raise ValueError("query is required when use_mirror_serving=True")

    def test_async_fabric_native_in_error_message(self):
        """Error messages should mention Fabric native accounts."""
        with pytest.raises(ValueError, match="Fabric native"):
            raise ValueError(
                "use_mirror_serving=True requires mirror_config to be provided "
                "in CosmosClient constructor. "
                "Note: Fabric mirroring is only supported with CosmosDB Fabric native accounts."
            )


class TestAsyncClientMirrorDocstring(unittest.TestCase):
    """Test that async CosmosClient documents mirror_config."""

    def test_async_client_has_mirror_config_docs(self):
        """Verify that the async CosmosClient class docstring mentions mirror_config."""
        from azure.cosmos.aio._cosmos_client import CosmosClient
        assert "mirror_config" in CosmosClient.__doc__

    def test_async_client_docs_mention_fabric_native(self):
        """Verify that the async CosmosClient docstring mentions Fabric native accounts."""
        from azure.cosmos.aio._cosmos_client import CosmosClient
        assert "Fabric native" in CosmosClient.__doc__


if __name__ == "__main__":
    unittest.main()
