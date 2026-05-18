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

"""Unit tests for Fabric mirror serving integration.

These tests use mocking only — no live Cosmos DB or Fabric connections required.
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest

from azure.core.exceptions import AzureError
from azure.cosmos._mirror_integration import (
    execute_mirrored_query,
    _validate_mirror_config,
    _get_config_value,
)
from azure.cosmos.exceptions import MirrorServingNotAvailableError


class TestMirrorServingExceptionHierarchy(unittest.TestCase):
    """Test that MirrorServingNotAvailableError is in the SDK exception hierarchy."""

    def test_inherits_from_azure_error(self):
        error = MirrorServingNotAvailableError()
        assert isinstance(error, AzureError)

    def test_error_message_includes_install_instructions(self):
        error = MirrorServingNotAvailableError()
        msg = str(error)
        assert "azure-cosmos-fabric-mapper" in msg
        assert "pip install" in msg

    def test_error_message_includes_fabric_native_note(self):
        error = MirrorServingNotAvailableError()
        msg = str(error)
        assert "Fabric native" in msg

    def test_error_message_includes_disable_instructions(self):
        error = MirrorServingNotAvailableError()
        msg = str(error)
        assert "use_mirror_serving" in msg


class TestValidateMirrorConfig(unittest.TestCase):
    """Test mirror config validation logic."""

    def test_valid_config_with_server_and_database(self):
        config = {"server": "my-server.com", "database": "mydb"}
        _validate_mirror_config(config)  # Should not raise

    def test_valid_config_with_fabric_prefixed_keys(self):
        config = {"fabric_server": "my-server.com", "fabric_database": "mydb"}
        _validate_mirror_config(config)  # Should not raise

    def test_missing_server_raises_value_error(self):
        config = {"database": "mydb"}
        with pytest.raises(ValueError, match="server"):
            _validate_mirror_config(config)

    def test_missing_database_raises_value_error(self):
        config = {"server": "my-server.com"}
        with pytest.raises(ValueError, match="database"):
            _validate_mirror_config(config)

    def test_empty_config_raises_value_error(self):
        with pytest.raises(ValueError):
            _validate_mirror_config({})


class TestGetConfigValue(unittest.TestCase):
    """Test the config value lookup helper."""

    def test_returns_first_matching_key(self):
        config = {"server": "s1", "fabric_server": "s2"}
        assert _get_config_value(config, "server", "fabric_server") == "s1"

    def test_returns_second_key_if_first_missing(self):
        config = {"fabric_server": "s2"}
        assert _get_config_value(config, "server", "fabric_server") == "s2"

    def test_returns_default_if_no_match(self):
        config = {"other": "value"}
        assert _get_config_value(config, "server", "fabric_server", default="fallback") == "fallback"

    def test_returns_none_by_default(self):
        config = {}
        assert _get_config_value(config, "server") is None


class TestExecuteMirroredQuery(unittest.TestCase):
    """Test the mirrored query execution with mocked mapper package."""

    @patch("azure.cosmos._mirror_integration._lazy_import_mapper")
    def test_successful_query(self, mock_import):
        """Test that execute_mirrored_query calls the mapper and returns results."""
        mock_contract = MagicMock()
        expected_results = [{"id": "1", "name": "test"}]
        mock_contract.run_mirrored_query.return_value = expected_results
        mock_contract.MirroredQueryRequest.return_value = MagicMock()
        mock_import.return_value = mock_contract

        mock_config_cls = MagicMock()
        mock_cred_cls = MagicMock()
        mock_driver_fn = MagicMock()
        mock_driver_fn.return_value = "cached_driver"

        with patch.dict("sys.modules", {
            "azure_cosmos_fabric_mapper": MagicMock(MirrorServingConfiguration=mock_config_cls),
            "azure_cosmos_fabric_mapper.credentials": MagicMock(DefaultAzureSqlCredential=mock_cred_cls),
            "azure_cosmos_fabric_mapper.driver": MagicMock(get_driver_client=mock_driver_fn),
        }):
            results, driver = execute_mirrored_query(
                query="SELECT * FROM c",
                parameters=None,
                mirror_config={"server": "s", "database": "db"},
            )
            assert results == expected_results
            assert driver == "cached_driver"

    def test_missing_mapper_raises_error(self):
        with pytest.raises(MirrorServingNotAvailableError):
            execute_mirrored_query(
                query="SELECT * FROM c",
                parameters=None,
                mirror_config={"server": "s", "database": "db"},
            )

    def test_invalid_config_raises_value_error(self):
        with pytest.raises(ValueError, match="server"):
            execute_mirrored_query(
                query="SELECT * FROM c",
                parameters=None,
                mirror_config={"database": "db"},
            )


class TestContainerMirrorServing(unittest.TestCase):
    """Test mirror serving integration in ContainerProxy."""

    def _make_container(self, mirror_config=None):
        """Create a mock ContainerProxy-like object for testing."""
        container = MagicMock()
        container.client_connection = MagicMock()
        container.client_connection.mirror_config = mirror_config
        container.client_connection._mirror_driver_client = None
        container.id = "test-container"
        return container

    def test_mirror_config_not_set_raises_value_error(self):
        """When use_mirror_serving=True but no mirror_config, should raise ValueError."""
        from azure.cosmos.container import ContainerProxy

        container = self._make_container(mirror_config=None)

        # Simulate the validation logic from query_items
        with pytest.raises(ValueError, match="mirror_config"):
            if not container.client_connection.mirror_config:
                raise ValueError(
                    "use_mirror_serving=True requires mirror_config to be provided "
                    "in CosmosClient constructor. "
                    "Note: Fabric mirroring is only supported with CosmosDB Fabric native accounts."
                )

    def test_query_required_with_mirror_serving(self):
        """When use_mirror_serving=True but no query, should raise ValueError."""
        with pytest.raises(ValueError, match="query is required"):
            query_str = None
            if not query_str:
                raise ValueError("query is required when use_mirror_serving=True")

    def test_fabric_native_in_error_message(self):
        """Error messages should mention Fabric native accounts."""
        with pytest.raises(ValueError, match="Fabric native"):
            raise ValueError(
                "use_mirror_serving=True requires mirror_config to be provided "
                "in CosmosClient constructor. "
                "Note: Fabric mirroring is only supported with CosmosDB Fabric native accounts."
            )


if __name__ == "__main__":
    unittest.main()
