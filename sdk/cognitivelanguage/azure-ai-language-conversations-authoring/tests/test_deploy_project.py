# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationAuthoringCreateDeploymentDetails
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
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
    def test_begin_deploy_project(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)
        
        project_name = "EmailAppEnglish"
        deployment_name = "deployment1"
        deployment_client = client.get_deployment_client(project_name, deployment_name)

        # Prepare request body
        body = ConversationAuthoringCreateDeploymentDetails(trained_model_label="ModelWithDG")

        # Start deployment
        poller = deployment_client.begin_deploy_project(body)
        result = poller.result()  # Wait for completion

        # Access operation-location for logging/debugging
        operation_location = poller._polling_method._initial_response.http_response.headers.get("operation-location", "Not found")
        status_code = poller._polling_method._initial_response.http_response.status_code

        print(f"Operation-Location: {operation_location}")
        print(f"Operation completed with status code: {status_code}")

        assert result is None
        assert poller.status() == "succeeded"
