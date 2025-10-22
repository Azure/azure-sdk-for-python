# ------------ ASYNC: train ------------

import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    TrainingJobDetails,
    TrainingMode,
    EvaluationDetails,
    EvaluationKind,
    TrainingJobResult,
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


class TestConversationsTrainAsync(TestConversationsAsync):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_train_project_async(self, authoring_endpoint, authoring_key):
        client = await self.create_client(authoring_endpoint, authoring_key)
        try:
            project_name = "Test-data-labels"
            project_client = client.get_project_client(project_name)

            # Arrange
            details = TrainingJobDetails(
                model_label="MyModel",
                training_mode=TrainingMode.STANDARD,
                training_config_version="2023-04-15",
                evaluation_options=EvaluationDetails(
                    kind=EvaluationKind.PERCENTAGE,
                    testing_split_percentage=20,
                    training_split_percentage=80,
                ),
            )

            # Act: begin train (LRO)
            poller = await project_client.project.begin_train(body=details)

            # Wait for completion and get the TrainingJobResult
            result: TrainingJobResult = await poller.result()

            # Prints for visibility
            print(f"Model Label: {result.model_label}")
            print(f"Training Config Version: {result.training_config_version}")
            print(f"Training Mode: {result.training_mode}")
            print(f"Training Status: {result.training_status}")
            print(f"Data Generation Status: {result.data_generation_status}")
            print(f"Evaluation Status: {result.evaluation_status}")
            print(f"Estimated End: {result.estimated_end_on}")
        finally:
            await client.close()
