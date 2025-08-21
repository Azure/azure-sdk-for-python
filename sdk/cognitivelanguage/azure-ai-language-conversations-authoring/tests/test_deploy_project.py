# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateDeploymentDetails,
    DeploymentState,
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
    def test_deploy_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)

        # Get project-scoped client
        project_name = "EmailApp"
        deployment_name = "staging0818"
        project_client = authoring_client.get_project_client(project_name)

        details = CreateDeploymentDetails(trained_model_label="Model1")

        # New signature: begin_deploy_project(deployment_name, body) -> LROPoller[DeploymentState]
        poller = project_client.deployment_operations.begin_deploy_project(
            deployment_name=deployment_name,
            body=details,
        )

        # Wait for completion and get final DeploymentState
        state: DeploymentState = poller.result()

        # Print key properties of the DeploymentState
        print(f"Deployment job_id: {state.job_id}")
        print(f"Created on: {state.created_on}")
        print(f"Last updated on: {state.last_updated_on}")
        print(f"Expires on: {state.expires_on}")
        print(f"Status: {state.status}")
        print(f"Warnings: {state.warnings}")
        print(f"Errors: {state.errors}")

        # Basic assertions
        assert state is not None
        assert state.job_id  # should be populated
        assert state.status in (
            "notStarted",
            "running",
            "succeeded",
            "failed",
            "cancelled",
            "cancelling",
            "partiallyCompleted",
        )
