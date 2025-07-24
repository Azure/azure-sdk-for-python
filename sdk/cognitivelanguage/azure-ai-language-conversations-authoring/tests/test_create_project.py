import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.authoring import AuthoringClient
from azure.ai.language.conversations.authoring.models import ConversationAuthoringCreateProjectDetails 

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer, 'conversations',
    conversations_endpoint="fake_resource.servicebus.windows.net/",
    conversations_key="fake_key"
)

class TestConversations(AzureRecordedTestCase):

# Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = AuthoringClient(endpoint, credential)
        return client

    ...

class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_conversation_prediction(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        # Access the project operation group separately 
        project_client = client.conversation_authoring_project 

        # Define project name and creation details 
        project_name = "MyPythonProject0723" 
        project_data = ConversationAuthoringCreateProjectDetails( 
            project_kind="Conversation", 
            project_name=project_name,
            language="en-us", 
            multilingual=True, 
            description="Project description" 
        ) 

        # Create the project 
        response = project_client.create_project( 
            project_name=project_name, 
            body=project_data 
        ) 

        # Print confirmation 
        print(f"Project created: {response.project_name}, Kind: {response.project_kind}, Language: {response.language}")