# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
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


class TestConversationsDeleteTrainedModelAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_trained_model_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "Test-data-labels"
            trained_model_label = "MyModel"

            project_client = client.get_project_client(project_name)

            captured = {}

            def capture_response(pipeline_response):
                captured["status_code"] = pipeline_response.http_response.status_code

            # Act
            await project_client.trained_model.delete_trained_model(
                trained_model_label,
                raw_response_hook=capture_response,
            )

            # Print & Assert
            status = captured.get("status_code")
            print(f"Delete Trained Model Response Status: {status}")
            assert status == 204, f"Expected 204, got {status}"
        finally:
            await client.close()
