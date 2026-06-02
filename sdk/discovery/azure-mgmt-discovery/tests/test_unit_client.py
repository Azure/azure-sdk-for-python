# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for azure-mgmt-discovery client.

These tests verify client configuration without making HTTP calls.
"""
from azure.mgmt.discovery import DiscoveryMgmtClient


class TestDiscoveryMgmtClientUnit:
    """Unit tests for Discovery management client initialization."""

    def test_client_has_expected_operations(self):
        """Test that client exposes expected operation groups."""
        from azure.identity import DefaultAzureCredential

        client = DiscoveryMgmtClient(
            credential=DefaultAzureCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
        )

        # Verify operation groups exist
        assert hasattr(client, "operations")
        assert hasattr(client, "workspaces")
        assert hasattr(client, "workspace_private_endpoint_connections")
        assert hasattr(client, "workspace_private_link_resources")
        assert hasattr(client, "bookshelves")
        assert hasattr(client, "bookshelf_private_endpoint_connections")
        assert hasattr(client, "bookshelf_private_link_resources")
        assert hasattr(client, "projects")
        assert hasattr(client, "storage_assets")
        assert hasattr(client, "storage_containers")
        assert hasattr(client, "tools")
        assert hasattr(client, "supercomputers")
        assert hasattr(client, "node_pools")
        assert hasattr(client, "chat_model_deployments")

    def test_client_api_version(self):
        """Test that client uses correct API version."""
        from azure.identity import DefaultAzureCredential

        client = DiscoveryMgmtClient(
            credential=DefaultAzureCredential(),
            subscription_id="00000000-0000-0000-0000-000000000000",
        )

        # Verify API version is set
        assert client._config.api_version == "2026-02-01-preview"
