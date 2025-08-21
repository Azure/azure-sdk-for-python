# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationAuthoringTrainingJobDetails,
    ConversationAuthoringTrainingMode,
    ConversationAuthoringEvaluationDetails,
    ConversationAuthoringEvaluationKind,
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAuthoringClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_create_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)

        # Get project-scoped client
        project_name = "EmailApp"
        project_client = authoring_client.get_project_client(project_name)

        # Define training job details
        training_job_details = ConversationAuthoringTrainingJobDetails(
            model_label="Model0803",
            training_mode=ConversationAuthoringTrainingMode.STANDARD,
            training_config_version="2023-04-15",
            evaluation_options=ConversationAuthoringEvaluationDetails(
                kind=ConversationAuthoringEvaluationKind.PERCENTAGE,
                testing_split_percentage=20,
                training_split_percentage=80,
            ),
        )

        # Start training
        poller = project_client.project_operations.begin_train(body=training_job_details)

        # Grab the initial response without waiting for the result
        initial_response = poller._polling_method._initial_response.http_response
        operation_location = initial_response.headers.get("operation-location", "Not found")
        status_code = initial_response.status_code

        print(f"Operation-Location: {operation_location}")
        print(f"Initial status code: {status_code}")

        # Assert it was accepted
        assert status_code == 202
        assert operation_location != "Not found"
