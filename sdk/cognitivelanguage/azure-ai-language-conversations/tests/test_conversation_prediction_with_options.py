import functools
from typing import cast

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionResult,
    ConversationPrediction,
    StringIndexType,
    DateTimeResolution,
    ConversationLanguageUnderstandingInput,
)

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    conversations_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_conversation_prediction_with_options(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        project_name = "EmailApp"
        deployment_name = "production"

        data = ConversationLanguageUnderstandingInput(
            conversation_input=ConversationAnalysisInput(
                conversation_item=TextConversationItem(
                    id="1", participant_id="participant1", text="Send an email to Carol about tomorrow's demo"
                )
            ),
            action_content=ConversationActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
                verbose=True,
            ),
        )

        action_result = client.analyze_conversation(data)

        action_result = cast(ConversationActionResult, action_result)

        prediction = action_result.result.prediction
        prediction = cast(ConversationPrediction, prediction)
        print(f"Top intent: {prediction.top_intent}")

        print("Intents:")
        for intent in prediction.intents:
            print(f"Category: {intent.category}")
            print(f"Confidence: {intent.confidence}")
            print()

        print("Entities:")
        for entity in prediction.entities:
            print(f"Category: {entity.category}")
            print(f"Text: {entity.text}")
            print(f"Offset: {entity.offset}")
            print(f"Length: {entity.length}")
            print(f"Confidence: {entity.confidence}")
            print()

            if entity.resolutions:
                for res in entity.resolutions:
                    # type-safe: only access attrs if it's a DateTimeResolution
                    if isinstance(res, DateTimeResolution):
                        print(f"Datetime Sub Kind: {res.date_time_sub_kind}")
                        print(f"Timex: {res.timex}")
                        print(f"Value: {res.value}")
                        print()

        assert prediction.top_intent == "SendEmail"
