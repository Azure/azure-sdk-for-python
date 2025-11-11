# pylint: disable=line-too-long,useless-suppression
import functools
from importlib import resources

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import AssignedDeploymentResource

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsDeployProjectSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_list_project_resources(self, authoring_endpoint, authoring_key):
        # Arrange
        client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"
        project_client = client.get_project_client(project_name)

        resources = list(project_client.project.list_project_resources())
        
        for resource in resources:
            assert resource.resource_id
            assert resource.region
