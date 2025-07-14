import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations import ConversationsClient
from azure.ai.language.conversations.models import *

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
        client = ConversationsClient(endpoint, credential)
        return client

    ...

class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_conversation_prediction(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        # Replace with your actual project/deployment if not using test proxy
        project_name = "EmailApp"
        deployment_name = "production"

        data = AnalyzeConversationTask(
            kind="Conversation",
            analysis_input=ConversationAnalysisInput(
                conversation_item={
                    "id": "1",
                    "participant_id": "participant1",
                    "text": "Send an email to Carol about tomorrow's demo"
                }
            ),
            parameters=ConversationLanguageUnderstandingAction(
                project_name=project_name,
                deployment_name=deployment_name,
                string_index_type=StringIndexType.UTF16CODE_UNIT
            )
        )

        result = client.analyze_conversation(data)
        prediction = result["result"]["prediction"]

        assert prediction["topIntent"] == "SendEmail"
        assert isinstance(prediction["intents"], list)
        assert isinstance(prediction["entities"], list)

        for intent in prediction["intents"]:
            assert "category" in intent
            assert "confidenceScore" in intent
            assert 0.0 <= intent["confidenceScore"] <= 1.0

        for entity in prediction["entities"]:
            assert "category" in entity
            assert "text" in entity
            assert "offset" in entity
            assert "length" in entity
            assert "confidenceScore" in entity

            if "resolutions" in entity:
                for resolution in entity["resolutions"]:
                    if resolution["@type"] == "DateTimeResolution":
                        assert "timex" in resolution
                        assert "value" in resolution