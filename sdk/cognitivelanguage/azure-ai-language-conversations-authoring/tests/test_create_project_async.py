import functools
import pytest

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.ai.language.conversations.authoring.aio import AuthoringClient
from azure.core.credentials import AzureKeyCredential

ConversationsAuthoringPreparer = functools.partial(
    PowerShellPreparer, 'conversationsauthoring',
    conversationsauthoring_endpoint="https://fake_resource.cognitiveservices.azure.com",
    conversationsauthoring_key="fake_key"
)

class TestConversationsAuthoringAsync(AzureRecordedTestCase):
    # Create the client instance for reuse in async tests
    async def create_client(self, AZURE_AUTHORING_ENDPOINT, AZURE_AUTHORING_KEY):
        credential = AzureKeyCredential(AZURE_AUTHORING_KEY)
        client = AuthoringClient(AZURE_AUTHORING_ENDPOINT, credential)
        return client

class TestConversationsAuthoringCaseAsync(TestConversationsAuthoringAsync):
    @ConversationsAuthoringPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_create_project_async(self, conversationsauthoring_endpoint, conversationsauthoring_key):
        # Create the async client
        print("test_conversationsauthoring_endpoint", conversationsauthoring_endpoint)
        print("test_conversationsauthoring_key", conversationsauthoring_key)
        client = await self.create_client(conversationsauthoring_endpoint, conversationsauthoring_key)

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

            # Validate response (assert attributes of AnalyzeConversationAuthoringProjectMetadata)
            assert response is not None  # Ensure the response is not None
            assert response.project_name == project_name  # Check that the project name matches
            assert response.language == project_data["language"]  # Check that the language matches
            assert response.project_kind == project_data["projectKind"]  # Check that the project kind matches

            # Print confirmation for debugging
            print(f"Project created successfully: {response.project_name}")