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
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = AuthoringClient(endpoint, credential)
        return client

class TestConversationsAuthoringCase(TestConversationsAuthoring):
    @ConversationsAuthoringPreparer()
    @recorded_by_proxy
    def test_create_project(self, conversationsauthoring_endpoint, conversationsauthoring_key):
        client = self.create_client(conversationsauthoring_endpoint, conversationsauthoring_key)

        # Define project data
        project_name = "MyNewProject"
        project_data = {
            "projectName": project_name,
            "language": "en",
            "projectKind": "Conversation",
            "description": "Project description",
            "multilingual": True
        }

        # Send request to create the project
        response = client.create_project(project_name, project_data)
        
        # Validate response
        assert response.status_code == 201
        print(f"Project created with status: {response.status_code}")