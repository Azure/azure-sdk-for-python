# pylint: disable=line-too-long,useless-suppression
import functools
from typing import cast
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationalAITask,
    ConversationalAIAnalysisInput,
    TextConversation,
    TextConversationItem,
    ConversationalAIActionContent,
    AnalyzeConversationActionResult,
    StringIndexType,
    ConversationalAITaskResult,
    ConversationalAIResult,
    ConversationalAIAnalysis,
    ConversationalAIIntent,
    ConversationalAIEntity,
    ConversationItemRange,
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
    async def test_conversation_multi_turn_prediction_async(self, conversations_endpoint, conversations_key):
        client = await self.create_client(conversations_endpoint, conversations_key)

        try:
            project_name = "EmailApp"
            deployment_name = "production"

            data = ConversationalAITask(
                analysis_input=ConversationalAIAnalysisInput(
                    conversations=[
                        TextConversation(
                            id="order",
                            language="en-GB",
                            conversation_items=[
                                TextConversationItem(id="1", participant_id="user", text="Hi"),
                                TextConversationItem(id="2", participant_id="bot", text="Hello, how can I help you?"),
                                TextConversationItem(
                                    id="3",
                                    participant_id="user",
                                    text="Send an email to Carol about tomorrow's demo",
                                ),
                            ],
                        )
                    ]
                ),
                parameters=ConversationalAIActionContent(
                    project_name=project_name,
                    deployment_name=deployment_name,
                    string_index_type=StringIndexType.UTF16_CODE_UNIT,
                ),
            )

            # Async call
            response: AnalyzeConversationActionResult = await client.analyze_conversation(data)

            # Cast to ConversationalAI task result
            ai_task_result = cast(ConversationalAITaskResult, response)
            ai_result: ConversationalAIResult = ai_task_result.result

            # Basic sanity
            assert ai_result is not None
            assert ai_result.conversations is not None

            # Iterate conversations
            for conversation in ai_result.conversations or []:
                conversation = cast(ConversationalAIAnalysis, conversation)
                print(f"Conversation ID: {conversation.id}\n")

                # Intents
                print("Intents:")
                for intent in conversation.intents or []:
                    intent = cast(ConversationalAIIntent, intent)
                    print(f"  Name: {intent.name}")
                    print(f"  Type: {getattr(intent, 'type', None)}")

                    print("  Conversation Item Ranges:")
                    for rng in intent.conversation_item_ranges or []:
                        rng = cast(ConversationItemRange, rng)
                        print(f"    - Offset: {rng.offset}, Count: {rng.count}")

                    print("\n  Entities (Scoped to Intent):")
                    for ent in intent.entities or []:
                        ent = cast(ConversationalAIEntity, ent)
                        print(f"    Name: {ent.name}")
                        print(f"    Text: {ent.text}")
                        print(f"    Confidence: {ent.confidence_score}")
                        print(f"    Offset: {ent.offset}, Length: {ent.length}")
                        print(
                            f"    Conversation Item ID: {ent.conversation_item_id}, "
                            f"Index: {ent.conversation_item_index}"
                        )

                    print()

                # Global entities
                print("Global Entities:")
                for ent in conversation.entities or []:
                    ent = cast(ConversationalAIEntity, ent)
                    print(f"  Name: {ent.name}")
                    print(f"  Text: {ent.text}")
                    print(f"  Confidence: {ent.confidence_score}")
                    print(f"  Offset: {ent.offset}, Length: {ent.length}")
                    print(
                        f"  Conversation Item ID: {ent.conversation_item_id}, " f"Index: {ent.conversation_item_index}"
                    )

                print("-" * 40)
        finally:
            await client.close()
