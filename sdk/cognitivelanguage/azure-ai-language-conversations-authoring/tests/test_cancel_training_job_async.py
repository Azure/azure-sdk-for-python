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


class TestConversationsCancelTrainingAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_cancel_training_job_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "Test-data-labels"
            job_id = "122b7341-afaa-4bea-af63-f6c7e0539fcb_638985888000000000"
            project_client = client.get_project_client(project_name)

            poller = await project_client.project.begin_cancel_training_job(
                job_id=job_id,
            )

            result = await poller.result()  # TrainingJobResult

            assert (
                result.training_status.status == "cancelled"
            ), f"Cancellation failed with status: {result.training_status.status}"

            print(f"Model Label: {result.model_label}")
            print(f"Training Config Version: {result.training_config_version}")
            print(f"Training Mode: {result.training_mode}")
            if result.data_generation_status is not None:
                print(f"Data Generation Status: {result.data_generation_status.status}")
                print(f"Data Generation %: {result.data_generation_status.percent_complete}")
            if result.training_status is not None:
                print(f"Training Status: {result.training_status.status}")
                print(f"Training %: {result.training_status.percent_complete}")
            if result.evaluation_status is not None:
                print(f"Evaluation Status: {result.evaluation_status.status}")
                print(f"Evaluation %: {result.evaluation_status.percent_complete}")
            print(f"Estimated End: {result.estimated_end_on}")
        finally:
            await client.close()
