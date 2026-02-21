# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import AssignedProjectResource

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsListProjectResourcesSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_list_project_resources(self, authoring_endpoint, authoring_key):
        # Arrange
        client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"
        project_client = client.get_project_client(project_name)

        # Act
        paged = project_client.project.list_project_resources()

        # Assert each resource item
        for res in paged:
            assert isinstance(res, AssignedProjectResource)
            assert isinstance(res.resource_id, str) and res.resource_id
            assert isinstance(res.region, str) and res.region
