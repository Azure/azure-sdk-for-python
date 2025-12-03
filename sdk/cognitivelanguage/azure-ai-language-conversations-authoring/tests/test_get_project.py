# pylint: disable=line-too-long,useless-suppression
import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectDetails

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "authoring",
    authoring_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    authoring_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    def create_client(self, endpoint, key):
        return ConversationAuthoringClient(endpoint, AzureKeyCredential(key))


class TestConversationsGetProjectSync(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_get_project(self, authoring_endpoint, authoring_key):
        authoring_client = self.create_client(authoring_endpoint, authoring_key)
        project_name = "EmailApp"

        # Act
        details = authoring_client.get_project(project_name=project_name)

        # Assert
        assert isinstance(details, ProjectDetails)
        assert details.project_name == project_name

        # Print like the C# sample
        print(f"Created DateTime: {details.created_on}")
        print(f"Last Modified DateTime: {details.last_modified_on}")
        print(f"Last Trained DateTime: {details.last_trained_on}")
        print(f"Last Deployed DateTime: {details.last_deployed_on}")
        print(f"Project Kind: {details.project_kind}")
        print(f"Project Name: {details.project_name}")
        print(f"Multilingual: {details.multilingual}")
        print(f"Description: {details.description}")
        print(f"Language: {details.language}")
