# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsLoadSnapshotPrintResultAsync(AzureRecordedTestCase):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_load_snapshot_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_name = "single-class-project"
            trained_model_label = "model3"

            project_client = client.get_project_client(project_name)

            # Start LRO and wait for completion
            poller = await project_client.trained_model.begin_load_snapshot(trained_model_label)
            try:
                await poller.result()  # completes with None; raises on failure
            except HttpResponseError as e:
                msg = getattr(getattr(e, "error", None), "message", str(e))
                print(f"Operation failed: {msg}")
                raise

            # Success -> poller completed
            print(f"Load snapshot completed. done={poller.done()} status={poller.status()}")
