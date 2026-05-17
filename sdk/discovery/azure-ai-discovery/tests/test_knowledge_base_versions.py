# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Knowledge Base Versions operations.

Covers all 9 methods on BookshelfClient.knowledge_base_versions:
  - create_or_update
  - get, get_latest_version
  - list (Paged)
  - get_operation_status
  - begin_start_indexing, begin_cancel_indexing (LRO)
  - delete, delete_latest_version
"""
import pytest
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.ai.discovery._bookshelf.azure.ai.discovery.models import KnowledgeBaseVersion, StorageAssetReference
from .testcase import DiscoveryBookshelfTestCase
from .constants import (
    KNOWLEDGE_BASE_NAME,
    KNOWLEDGE_BASE_VERSION,
    KNOWLEDGE_BASE_CREATE_NAME,
    KNOWLEDGE_BASE_DESCRIPTION,
    KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
    STORAGE_ASSET_ID,
    USER_ASSIGNED_IDENTITY,
    NODE_POOL_ID,
    BOOKSHELF_NODE_POOL_ID,
    PROJECT_NAME,
    PROJECT_ARM_ID,
)


class TestKnowledgeBaseVersionsOperations(DiscoveryBookshelfTestCase):
    """Tests for KnowledgeBaseVersionsOperations."""

    @recorded_by_proxy
    def test_create_or_update(self):
        """Test creating or updating a knowledge base version."""
        client = self.create_bookshelf_client()
        version = client.knowledge_base_versions.create_or_update(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            version_name=KNOWLEDGE_BASE_VERSION,
            resource=KnowledgeBaseVersion(
                description=KNOWLEDGE_BASE_DESCRIPTION,
                copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                storage_asset_references=[
                    StorageAssetReference(
                        id=STORAGE_ASSET_ID,
                        user_assigned_identity=USER_ASSIGNED_IDENTITY,
                    )
                ],
            ),
        )
        assert version is not None
        assert version.description == KNOWLEDGE_BASE_DESCRIPTION

    @recorded_by_proxy
    def test_list(self):
        """Test listing knowledge base versions."""
        client = self.create_bookshelf_client()
        versions = list(
            client.knowledge_base_versions.list(knowledge_base_name=KNOWLEDGE_BASE_NAME)
        )
        assert isinstance(versions, list)
        assert len(versions) > 0
        for v in versions:
            assert v.version is not None
            assert v.provisioning_state is not None

    @recorded_by_proxy
    def test_get(self):
        """Test getting a specific knowledge base version."""
        client = self.create_bookshelf_client()
        version = client.knowledge_base_versions.get(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            version_name=KNOWLEDGE_BASE_VERSION,
        )
        assert version is not None
        assert version.version == KNOWLEDGE_BASE_VERSION
        assert version.bookshelf_name is not None
        assert version.provisioning_state is not None
        assert version.created_at is not None
        assert version.description == KNOWLEDGE_BASE_DESCRIPTION
        assert version.copilot_instruction is not None
        assert isinstance(version.storage_asset_references, list)

    @recorded_by_proxy
    def test_get_latest_version(self):
        """Test getting the latest version of a knowledge base."""
        client = self.create_bookshelf_client()
        latest = client.knowledge_base_versions.get_latest_version(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
        )
        assert latest is not None
        assert latest.version is not None
        assert latest.bookshelf_name is not None
        assert latest.provisioning_state is not None

    @recorded_by_proxy
    def test_get_operation_status(self):
        """Test getting operation status for a knowledge base version.

        Starts an indexing LRO to obtain a real operation ID, checks its status,
        then cancels the indexing to clean up.
        """
        client = self.create_bookshelf_client()

        # Start indexing to get a real operation ID
        poller = client.knowledge_base_versions.begin_start_indexing(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            version_name=KNOWLEDGE_BASE_VERSION,
            node_pool_id=NODE_POOL_ID, # BOOKSHELF_
            project_id=PROJECT_ARM_ID,
            polling=False,
        )
        # Extract operation ID from the Operation-Location header
        initial_response = poller._polling_method._initial_response
        op_location = initial_response.http_response.headers.get("operation-location", "")
        operation_id = op_location.split("/operations/")[-1].split("?")[0]
        assert operation_id, "Could not extract operation_id from Operation-Location header"

        # Act — check the operation status
        status = client.knowledge_base_versions.get_operation_status(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            version_name=KNOWLEDGE_BASE_VERSION,
            operation_id=operation_id,
        )
        assert status is not None
        assert status["status"] is not None

        # Cleanup — cancel the indexing
        client.knowledge_base_versions.begin_cancel_indexing(
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            version_name=KNOWLEDGE_BASE_VERSION,
            node_pool_id=NODE_POOL_ID, # BOOKSHELF_
            polling=False,
        )

    @recorded_by_proxy
    def test_begin_delete(self):
        """Test deleting a specific knowledge base version (LRO).

        Creates a sacrificial version on the throwaway KB so the read
        tests' fixtures (KNOWLEDGE_BASE_NAME / KNOWLEDGE_BASE_VERSION)
        are never touched.
        """
        client = self.create_bookshelf_client()
        sacrificial_version = "delv1"

        # Create the version we will delete
        client.knowledge_base_versions.create_or_update(
            knowledge_base_name="sdktestdelv1",
            version_name=sacrificial_version,
            resource=KnowledgeBaseVersion(
                description="Sacrificial KB version for delete test",
                copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                storage_asset_references=[
                    StorageAssetReference(
                        id=STORAGE_ASSET_ID,
                        user_assigned_identity=USER_ASSIGNED_IDENTITY,
                    )
                ],
            ),
        )

        poller = client.knowledge_base_versions.begin_delete(
            knowledge_base_name="sdktestdelv1",
            version_name=sacrificial_version,
        )
        result = poller.result()
        assert result is not None


    @recorded_by_proxy
    def test_begin_delete_latest_version(self):
        """Test deleting the latest version of a knowledge base (LRO).

        Creates a sacrificial KB version so this test owns the 'latest' it
        deletes.
        """
        client = self.create_bookshelf_client()
        sacrificial_version = "delv2"

        client.knowledge_base_versions.create_or_update(
            knowledge_base_name="sdktestdelv2",
            version_name=sacrificial_version,
            resource=KnowledgeBaseVersion(
                description="Sacrificial KB version for delete-latest test",
                copilot_instruction=KNOWLEDGE_BASE_COPILOT_INSTRUCTION,
                storage_asset_references=[
                    StorageAssetReference(
                        id=STORAGE_ASSET_ID,
                        user_assigned_identity=USER_ASSIGNED_IDENTITY,
                    )
                ],
            ),
        )

        poller = client.knowledge_base_versions.begin_delete_latest_version(
            knowledge_base_name="sdktestdelv2",
        )
        result = poller.result()
        assert result is not None
