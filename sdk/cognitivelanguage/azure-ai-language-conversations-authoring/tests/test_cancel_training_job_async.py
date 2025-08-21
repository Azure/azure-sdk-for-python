# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import TrainingJobResult

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsAsync(AzureRecordedTestCase):
    async def create_client(self, endpoint: str, key: str) -> ConversationAuthoringClient:
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsCancelTrainingAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_cancel_training_job_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "Test-data-labels"
            job_id = "57fe7f38-7f74-4169-9133-95de6a223e6f_638913312000000000"
            project_client = client.get_project_client(project_name)

            captured = {}

            def capture_initial_response(pipeline_response):
                http_resp = pipeline_response.http_response
                captured["status_code"] = http_resp.status_code
                captured["headers"] = http_resp.headers

            # Start cancel; no polling; capture initial response via hook.
            poller = await project_client.project.begin_cancel_training_job(
                job_id=job_id,
                polling=False,
                raw_response_hook=capture_initial_response,
            )

            # Assert initial HTTP status
            assert captured.get("status_code") == 202, f"Expected 202, got {captured.get('status_code')}"

            # Print polling endpoints from headers
            headers = captured.get("headers", {})
            print(f"Operation-Location: {headers.get('Operation-Location') or headers.get('operation-location')}")
            print(f"Location: {headers.get('Location') or headers.get('location')}")

            assert poller is not None
        finally:
            await client.close()
