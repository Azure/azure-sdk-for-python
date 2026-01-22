# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    # Keeping the base class for parity; not used directly in this async test.
    def create_client(self, endpoint: str, key: str) -> TextAuthoringClient:  # type: ignore[override]
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))  # type: ignore[arg-type]

@pytest.mark.playback_test_only
class TestConversationsCaseAsync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_project_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "MyTextPythonProject0728"

            # Act: begin delete (LRO)
            poller = await client.begin_delete_project(project_name)

            try:
                await poller.result()
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            # If we get here, the delete succeeded
            print(f"Delete completed. done={poller.done()} status={poller.status()}")
