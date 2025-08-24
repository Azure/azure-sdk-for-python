import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    AnalyzeConversationOperationInput,
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionResult,
    ConversationPrediction,
    ConversationIntent,
    ConversationEntity,
    StringIndexType,
    ResolutionBase,
    DateTimeResolution,
    ConversationLanguageUnderstandingInput,
)
from typing import cast
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.async_paging import AsyncItemPaged

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
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
    async def test_conversation_prediction_with_options_async(self, conversations_endpoint, conversations_key):
        client = await self.create_client(conversations_endpoint, conversations_key)

        try:
            project_name = "EmailApp"
            deployment_name = "production"

            data = ConversationLanguageUnderstandingInput(
                conversation_input=ConversationAnalysisInput(
                    conversation_item=TextConversationItem(
                        id="1",
                        participant_id="participant1",
                        text="Send an email to Carol about tomorrow's demo",
                    )
                ),
                action_content=ConversationActionContent(
                    project_name=project_name,
                    deployment_name=deployment_name,
                    string_index_type=StringIndexType.UTF16_CODE_UNIT,
                    verbose=True,
                ),
            )

            action_result = await client.analyze_conversation(data)
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
        finally:
            await client.close()
