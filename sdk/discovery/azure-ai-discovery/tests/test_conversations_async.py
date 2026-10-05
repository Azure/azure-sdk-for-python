# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async tests for Conversations operations.

Mirrors test_conversations.py against the async ``WorkspaceClient`` from
``azure.ai.discovery.aio``.
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.discovery.models import Conversation
from .testcase import DiscoveryWorkspaceTestCase
from .constants import investigation_path


class TestConversationsAsync(DiscoveryWorkspaceTestCase):
    """Async tests for ConversationsOperations."""

    test_conversation_id = "00000000-0000-0000-0000-000000000000"

    @recorded_by_proxy_async
    async def test_create(self):
        client = self.create_async_workspace_client()
        async with client:
            investigation_path_str = investigation_path(self.project_name, self.investigation_name)
            conversation = await client.conversations.create(
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
            TestConversationsAsync.test_conversation_id = conversation.name

    @recorded_by_proxy_async
    async def test_list(self):
        """``conversations.list`` returns a ``PagedConversation`` envelope.
        Iterate ``.value``."""
        found_test_conversation_id = False
        client = self.create_async_workspace_client()
        async with client:
            page = await client.conversations.list(project_name=self.project_name)
            assert page.value is not None
            assert len(page.value) > 0
            for conv in page.value:
                assert conv.project_name == self.project_name
                assert conv.created_at is not None
                assert conv.investigation_name is not None
                if conv.name == TestConversationsAsync.test_conversation_id:
                    found_test_conversation_id = True
            assert found_test_conversation_id

    @recorded_by_proxy_async
    async def test_get(self, **kwargs):
        variables = kwargs.pop("variables", {})
        client = self.create_async_workspace_client()
        async with client:
            if "conversation_name" not in variables:
                investigation_path_str = investigation_path(self.project_name, self.investigation_name)
                created = await client.conversations.create(
                    body=Conversation(
                        display_name="Conversation for get test",
                        project_name=self.project_name,
                        investigation_name=investigation_path_str,
                    ),
                )
                variables["conversation_name"] = created.name

            conversation = await client.conversations.get(
                conversation_name=variables["conversation_name"],
            )
            assert conversation is not None
            assert conversation.name is not None
            assert conversation.project_name == self.project_name
            assert conversation.created_at is not None

    @recorded_by_proxy_async
    async def test_stable_update(self):
        client = self.create_async_workspace_client()
        async with client:
            updated = await client.conversations.stable_update(
                conversation_name=TestConversationsAsync.test_conversation_id,
                resource=Conversation(display_name="Updated conversation"),
            )
            assert updated is not None
            assert updated.display_name == "Updated conversation"
            assert updated.last_modified_at is not None

    @recorded_by_proxy_async
    async def test_delete(self):
        client = self.create_async_workspace_client()
        async with client:
            status = await client.conversations.delete(
                conversation_name=TestConversationsAsync.test_conversation_id,
            )
            assert status is None
