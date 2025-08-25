# ---------- ASYNC ----------

import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectDeletionState  # optional (type hint only)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeleteProjectAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "PythonImportProject0820"
            # Act: begin delete (LRO)
            poller = await client.begin_delete_project(project_name)

            # Wait for completion and get the ProjectDeletionState
            result = await poller.result()

            assert result.status == "succeeded", f"Deletion failed with status: {result.status}"
            # Print details of the ProjectDeletionState
            print(f"Job ID: {result.job_id}")
            print(f"Status: {result.status}")
            print(f"Created on: {result.created_on}")
            print(f"Last updated on: {result.last_updated_on}")
            print(f"Expires on: {result.expires_on}")
            print(f"Warnings: {result.warnings}")
            print(f"Errors: {result.errors}")
        finally:
            await client.close()
