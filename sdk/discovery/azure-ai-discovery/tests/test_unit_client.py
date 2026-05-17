# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for azure-ai-discovery clients.

These tests verify client configuration without making HTTP calls.
"""
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.discovery import WorkspaceClient, BookshelfClient


class TestWorkspaceClientUnit:
    """Unit tests for Workspace client initialization."""

    def test_client_initialization(self):
        """Test that client can be initialized with endpoint and credential."""
        # Create client with fake endpoint (won't make HTTP calls)
        client = WorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify client is created
        assert client is not None

    def test_client_has_expected_operations(self):
        """Test that client exposes expected operation groups."""
        client = WorkspaceClient(
            endpoint="https://fake-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify operation groups exist
        assert hasattr(client, "conversations")
        assert hasattr(client, "tasks")
        assert hasattr(client, "investigations")
        assert hasattr(client, "tools")

    def test_client_endpoint_validation(self):
        """Test that client accepts valid endpoint URLs."""
        # Valid HTTPS endpoint
        client = WorkspaceClient(
            endpoint="https://my-workspace.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )
        assert client is not None


class TestBookshelfClientUnit:
    """Unit tests for Bookshelf client initialization."""

    def test_client_initialization(self):
        """Test that client can be initialized with endpoint and credential."""
        # Create client with fake endpoint (won't make HTTP calls)
        client = BookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify client is created
        assert client is not None

    def test_client_has_expected_operations(self):
        """Test that client exposes expected operation groups."""
        client = BookshelfClient(
            endpoint="https://fake-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )

        # Verify operation groups exist
        assert hasattr(client, "knowledge_bases")
        assert hasattr(client, "knowledge_base_versions")

    def test_client_endpoint_validation(self):
        """Test that client accepts valid endpoint URLs."""
        # Valid HTTPS endpoint
        client = BookshelfClient(
            endpoint="https://my-bookshelf.discovery.azure.com",
            credential=AzureKeyCredential("fake-key"),
        )
        assert client is not None
