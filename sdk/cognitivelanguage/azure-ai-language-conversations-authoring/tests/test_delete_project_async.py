# ---------- ASYNC ----------

import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient

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
        async with client:
            project_name = "PythonImportProject0820"

            # Begin delete; LRO now returns None on success
            poller = await client.begin_delete_project(project_name)

            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                print(f"Operation failed: {e.message}")
                print(e.error)
                raise

            # Success -> poller completed
            print(f"Delete completed. done={poller.done()} status={poller.status()}")
