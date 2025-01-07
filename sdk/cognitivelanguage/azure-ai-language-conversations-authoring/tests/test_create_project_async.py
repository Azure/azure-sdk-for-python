import pytest
import functools

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import AuthoringClient

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

class TestConversationsAuthoringAsync(TestConversationsAuthoring):
    @ConversationsAuthoringPreparer()
    @recorded_by_proxy_async
    async def test_create_project_async(self, conversationsauthoring_endpoint, conversationsauthoring_key):
        # Create the client
        client = self.create_client(conversationsauthoring_endpoint, conversationsauthoring_key)

        async with client:
            # Define project data
            project_name = "MyNewProjectAsync"
            project_data = {
                "projectName": project_name,
                "language": "en",
                "projectKind": "Conversation",
                "description": "Project description",
                "multilingual": True
            }

            # Send request to create the project
            response = await client.analyze_conversation_authoring.create_project(
                project_name=project_name,
                body=project_data
            )

            # Validate response
            assert response is not None
            assert response.project_name == project_name
            assert response.language == project_data["language"]
            assert response.project_kind == project_data["projectKind"]

            print(f"Project created successfully: {response.project_name}")