# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Unit tests for azure-mgmt-discovery models.

These tests verify model initialization without making HTTP calls.
"""
from azure.mgmt.discovery import models


class TestDiscoveryModelsUnit:
    """Unit tests for Discovery management SDK models."""

    def test_workspace_model_initialization(self):
        """Test Workspace model can be initialized."""
        workspace = models.Workspace(
            location="eastus",
            properties=models.WorkspaceProperties(),
        )
        assert workspace.location == "eastus"
        assert workspace.properties is not None

    def test_identity_model(self):
        """Test Identity model can be initialized."""
        identity = models.Identity(
            id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id",
        )
        assert (
            identity.id
            == "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/id"
        )

    def test_bookshelf_model_initialization(self):
        """Test Bookshelf model can be initialized."""
        bookshelf = models.Bookshelf(
            location="eastus",
            properties=models.BookshelfProperties(),
        )
        assert bookshelf.location == "eastus"
        assert bookshelf.properties is not None

    def test_project_model_initialization(self):
        """Test Project model can be initialized."""
        project = models.Project(
            location="eastus",
            properties=models.ProjectProperties(),
        )
        assert project.location == "eastus"
        assert project.properties is not None

    def test_storage_asset_model_initialization(self):
        """Test StorageAsset model can be initialized."""
        storage = models.StorageAsset(
            location="eastus",
            properties=models.StorageAssetProperties(),
        )
        assert storage.location == "eastus"
        assert storage.properties is not None

    def test_storage_container_model_initialization(self):
        """Test StorageContainer model can be initialized."""
        container = models.StorageContainer(
            properties=models.StorageContainerProperties(),
        )
        assert container.properties is not None

    def test_tool_model_initialization(self):
        """Test Tool model can be initialized."""
        tool = models.Tool(
            location="eastus",
            properties=models.ToolProperties(),
        )
        assert tool.location == "eastus"
        assert tool.properties is not None

    def test_supercomputer_model_initialization(self):
        """Test Supercomputer model can be initialized."""
        supercomputer = models.Supercomputer(
            location="eastus",
            properties=models.SupercomputerProperties(),
        )
        assert supercomputer.location == "eastus"
        assert supercomputer.properties is not None

    def test_node_pool_model_initialization(self):
        """Test NodePool model can be initialized."""
        node_pool = models.NodePool(
            properties=models.NodePoolProperties(),
        )
        assert node_pool.properties is not None
