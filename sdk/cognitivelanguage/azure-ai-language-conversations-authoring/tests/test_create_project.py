import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import AuthoringClient
from azure.core.credentials import AzureKeyCredential

ConversationsAuthoringPreparer = functools.partial(
    PowerShellPreparer, 'conversationsauthoring',
    conversationsauthoring_endpoint="fake_resource.cognitiveservices.azure.com/",
    conversationsauthoring_key="fake_key"
)

class TestConversationsAuthoring(AzureRecordedTestCase):
    # Create the client instance for reuse in tests
    def create_client(self, AZURE_AUTHORING_ENDPOINT, AZURE_AUTHORING_KEY):
        credential = AzureKeyCredential(AZURE_AUTHORING_KEY)
        client = AuthoringClient(AZURE_AUTHORING_ENDPOINT, credential)
        return client

class TestConversationsAuthoringCase(TestConversationsAuthoring):
    @ConversationsAuthoringPreparer()
    @recorded_by_proxy
    def test_create_project(self, conversationsauthoring_endpoint, conversationsauthoring_key):
        # Create the client
        client = self.create_client(conversationsauthoring_endpoint, conversationsauthoring_key)

        # Define project data
        project_name = "MyNewProject001"
        project_data = {
            "projectName": project_name,
            "language": "en",
            "projectKind": "Conversation",
            "description": "Project description",
            "multilingual": True
        }

        # Send request to create the project
        response = client.analyze_conversation_authoring.create_project(
            project_name=project_name,
            body=project_data
        )
        
        # Validate response (assert attributes of AnalyzeConversationAuthoringProjectMetadata)
        assert response is not None  # Ensure the response is not None
        assert response.project_name == project_name  # Check that the project name matches
        assert response.language == project_data["language"]  # Check that the language matches
        assert response.project_kind == project_data["projectKind"]  # Check that the project kind matches

        # Print confirmation for debugging
        print(f"Project created successfully: {response.project_name}")