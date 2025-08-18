import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    AnalyzeConversationOperationInput,
    ConversationLanguageUnderstandingActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionResult,
    ConversationPrediction,
    ConversationIntent,
    ConversationEntity,
    StringIndexType,
    ResolutionBase,
    DateTimeResolution,
    AnalyzeConversationActionResult,
    ConversationLanguageUnderstandingInput,
)
from typing import cast

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "conversations",
    conversations_endpoint="fake_resource.servicebus.windows.net/",
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
    def test_conversation_prediction(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        project_name = "EmailApp"
        deployment_name = "production"

        # Build request using strongly-typed models; set language to Spanish ("es")
        data = ConversationLanguageUnderstandingInput(
            conversation_input=ConversationAnalysisInput(
                conversation_item=TextConversationItem(
                    id="1",
                    participant_id="participant1",
                    text="Enviar un email a Carol acerca de la presentación de mañana",
                    language="es",
                )
            ),
            action_content=ConversationLanguageUnderstandingActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
                verbose=True,
            ),
        )

        # Call API
        response: AnalyzeConversationActionResult = client.analyze_conversation(data)

        # Cast to discriminator subtype (C#: `as ConversationActionResult`)
        conversation_result = cast(ConversationActionResult, response)
        prediction = conversation_result.result.prediction
        assert isinstance(prediction, ConversationPrediction)

        print(f"Top intent: {prediction.top_intent}")

        # Intents
        print("Intents:")
        for intent in prediction.intents or []:
            print(f"Category: {intent.category}")
            print(f"Confidence: {intent.confidence}")
            print()

        # Entities
        print("Entities:")
        for entity in prediction.entities or []:
            print(f"Category: {entity.category}")
            print(f"Text: {entity.text}")
            print(f"Offset: {entity.offset}")
            print(f"Length: {entity.length}")
            print(f"Confidence: {entity.confidence}")
            print()

            if entity.resolutions:
                for res in entity.resolutions:
                    if isinstance(res, DateTimeResolution):
                        print(f"Datetime Sub Kind: {getattr(res, 'date_time_sub_kind', None)}")
                        print(f"Timex: {res.timex}")
                        print(f"Value: {res.value}")
                        print()

        # Final assertion (mirror C#)
        assert prediction.top_intent == "SendEmail"
