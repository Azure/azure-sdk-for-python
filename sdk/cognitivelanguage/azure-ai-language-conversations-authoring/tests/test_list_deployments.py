# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationAuthoringProjectDeployment
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
    def test_list_deployments(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)

        project_name = "EmailApp"  # Replace with actual project name that has deployments
        deployments = client.list_deployments(project_name)

        assert deployments is not None

        for deployment in deployments:
            assert isinstance(deployment, ConversationAuthoringProjectDeployment)
            assert deployment.deployment_name is not None
            print(f"Deployment: {deployment.deployment_name}, model: {deployment.model_id}")
