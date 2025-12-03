# pylint: disable=line-too-long,useless-suppression
import functools
import json
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.authoring.aio import TextAuthoringClient

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversationsCancelTrainingAsync(AzureRecordedTestCase):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_cancel_training_job_async(self, authoring_endpoint, authoring_key):
        async with TextAuthoringClient(authoring_endpoint, AzureKeyCredential(authoring_key)) as client:
            project_client = client.get_project_client("single-class-project")
            job_id = "983d4481-b5c4-40dd-8d23-1ca159890e2f_638931456000000000"

            poller = await project_client.project.begin_cancel_training_job(
                job_id=job_id,
            )

            result = await poller.result()  # TrainingJobResult

            assert (
                result.training_status.status == "succeeded"
            ), f"Cancellation failed with status: {result.training_status.status}"
            print(f"Model Label: {result.model_label}")
            print(f"Training Config Version: {result.training_config_version}")
            if result.training_status is not None:
                print(f"Training Status: {result.training_status.status}")
                print(f"Training %: {result.training_status.percent_complete}")
            if result.evaluation_status is not None:
                print(f"Evaluation Status: {result.evaluation_status.status}")
                print(f"Evaluation %: {result.evaluation_status.percent_complete}")
            print(f"Estimated End: {result.estimated_end_on}")
