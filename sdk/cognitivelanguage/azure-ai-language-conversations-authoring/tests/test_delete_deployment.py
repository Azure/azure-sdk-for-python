# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

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
    def test_delete_deployment(self, authoring_endpoint, authoring_key):
        client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailAppEnglish"
        deployment_name = "assignedDeployment"
        deployment_client = client.get_deployment(project_name, deployment_name)

        # Act
        poller = deployment_client.begin_delete_deployment()
        result = poller.result()

        # Assert
        assert result is None
        print(f"Deleted deployment: {deployment_name} from project: {project_name}")
