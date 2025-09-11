# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient
from azure.ai.textanalytics.authoring.models import StringIndexType

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint: str, key: str) -> TextAuthoringClient:  # type: ignore[override]
        return TextAuthoringClient(endpoint, AzureKeyCredential(key))  # type: ignore[arg-type]


class TestConversationsCaseAsync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_export_project_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "single-class-project"
            project_client = client.get_project_client(project_name)

            # Act – LRO export
            poller = await project_client.project.begin_export(
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
            )

            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            # Success -> poller completed
            print(f"Export completed. done={poller.done()} status={poller.status()}")
