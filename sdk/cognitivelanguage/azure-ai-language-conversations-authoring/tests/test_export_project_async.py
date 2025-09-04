# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ExportedProjectFormat,
)

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsExportCaseAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_export_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        async with client:
            project_name = "Test-data-labels"
            project_client = client.get_project_client(project_name)

            # Act: begin export (LRO)
            poller = await project_client.project.begin_export(
                string_index_type="Utf16CodeUnit",
                exported_project_format=ExportedProjectFormat.CONVERSATION,
            )

            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                print(f"Operation failed: {e.message}")
                print(e.error)
                raise

            # Success -> poller completed
            print(f"Export completed. done={poller.done()} status={poller.status()}")
