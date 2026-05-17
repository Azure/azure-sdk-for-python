# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Conversations operations.

Covers all 5 methods on WorkspaceClient.conversations:
  - get, create, update, delete
  - list (Paged)
"""
import pytest
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.ai.discovery._workspace.azure.ai.discovery.models import Conversation
from .testcase import DiscoveryWorkspaceTestCase
from .constants import investigation_path

class TestConversations(DiscoveryWorkspaceTestCase):
    """Tests for ConversationsOperations."""

    test_conversation_id = "00000000-0000-0000-0000-000000000000"

    @recorded_by_proxy
    def test_create(self):
        """Test creating a conversation."""
        client = self.create_workspace_client()
        investigation_path_str = investigation_path(self.project_name, self.investigation_name)
        conversation = client.conversations.create(
            body=Conversation(
                display_name="Test conversation",
                project_name=self.project_name,
                investigation_name=investigation_path_str,
            ),
        )
        assert conversation is not None
        assert conversation.project_name == self.project_name
        assert conversation.name is not None
        assert conversation.created_at is not None
        # Save the id of the created conversation to use in subsequent tests
        TestConversations.test_conversation_id = conversation.name

    @recorded_by_proxy
    def test_list(self):
        """Test listing conversations."""
        found_test_conversation_id = False
        client = self.create_workspace_client()
        conversations = list(client.conversations.list(project_name=self.project_name))
        assert isinstance(conversations, list)
        assert len(conversations) > 0
        for conv in conversations:
            assert conv.project_name == self.project_name
            assert conv.created_at is not None
            assert conv.investigation_name is not None
            if conv.name == TestConversations.test_conversation_id:
                found_test_conversation_id = True
        # Verify that conversation created in test_create appears in list results
        assert found_test_conversation_id

    @recorded_by_proxy
    def test_get(self, **kwargs):
        """Test getting a specific conversation."""
        variables = kwargs.pop("variables", {})
        client = self.create_workspace_client()

        # During recording, create a conversation and store the name.
        # During playback, reuse the stored name.
        if "conversation_name" not in variables:
            investigation_path_str = investigation_path(self.project_name, self.investigation_name)
            created = client.conversations.create(
                body=Conversation(
                    display_name="Conversation for get test",
                    project_name=self.project_name,
                    investigation_name=investigation_path_str,
                ),
            )
            variables["conversation_name"] = created.name

        conversation = client.conversations.get(
            conversation_name=variables["conversation_name"],
        )
        assert conversation is not None
        assert conversation.name is not None
        assert conversation.project_name == self.project_name
        assert conversation.created_at is not None

    @recorded_by_proxy
    def test_update(self):
        """Test updating a conversation (PATCH)."""
        client = self.create_workspace_client()
        updated = client.conversations.update(
            conversation_name=TestConversations.test_conversation_id,
            resource=Conversation(display_name="Updated conversation"),
        )
        assert updated is not None
        assert updated.display_name == "Updated conversation"
        assert updated.last_modified_at is not None

    @recorded_by_proxy
    def test_delete(self):
        """Test deleting a conversation."""
        client = self.create_workspace_client()
        status = client.conversations.delete(conversation_name=TestConversations.test_conversation_id)
        assert status is None