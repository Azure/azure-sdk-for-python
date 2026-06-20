import functools
from typing import cast

import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionResult,
    ConversationPrediction,
    StringIndexType,
    DateTimeResolution,
    ConversationLanguageUnderstandingInput,
    AnalyzeConversationActionResult,
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
    async def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_conversation_prediction_with_language_async(self, conversations_endpoint, conversations_key):
        client = await self.create_client(conversations_endpoint, conversations_key)
        try:
            project_name = "EmailApp"
            deployment_name = "production"

            data = ConversationLanguageUnderstandingInput(
                conversation_input=ConversationAnalysisInput(
                    conversation_item=TextConversationItem(
                        id="1",
                        participant_id="participant1",
                        text="Enviar un email a Carol acerca de la presentación de mañana",
                        language="es",
                    )
                ),
                action_content=ConversationActionContent(
                    project_name=project_name,
                    deployment_name=deployment_name,
                    string_index_type=StringIndexType.UTF16_CODE_UNIT,
                    verbose=True,
                ),
            )

            # Async call
            response: AnalyzeConversationActionResult = await client.analyze_conversation(data)

            # Narrow to the discriminator subtype (C#-style cast)
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
        finally:
            await client.close()
