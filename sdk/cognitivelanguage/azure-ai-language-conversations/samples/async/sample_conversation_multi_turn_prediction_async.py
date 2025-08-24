# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_multi_turn_prediction_async.py

DESCRIPTION:
    This sample demonstrates how to run a multi-turn conversation prediction asynchronously
    using the Conversational AI task. It sends a short dialog (user ↔ bot ↔ user) to a
    CLU Conversation project and prints intents and entities, including spans,
    datetime resolutions, and subtype/tag metadata.

USAGE:
    python sample_conversation_multi_turn_prediction_async.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME
"""

# [START conversation_multi_turn_prediction_async]
import os
import asyncio
from typing import cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    # Request
    ConversationalAITask,
    ConversationalAIAnalysisInput,
    ConversationalAIActionContent,
    TextConversation,
    TextConversationItem,
    StringIndexType,
    # Response/result discriminators
    AnalyzeConversationActionResult,
    ConversationalAITaskResult,
    ConversationalAIResult,
    ConversationalAIAnalysis,
    ConversationalAIIntent,
    ConversationalAIEntity,
    ConversationItemRange,
    DateTimeResolution,
    EntitySubtype,
    EntityTag,
)


async def sample_conversation_multi_turn_prediction_async():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    try:
        # Build a small multi-turn dialog
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

        if not ai_result or not ai_result.conversations:
            print("No conversations found in result.")
            return

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

                    # Date/time resolutions
                    if ent.resolutions:
                        for res in ent.resolutions:
                            if isinstance(res, DateTimeResolution):
                                print(
                                    f"    - [DateTimeResolution] SubKind: {getattr(res, 'date_time_sub_kind', None)}, "
                                    f"Timex: {res.timex}, Value: {res.value}"
                                )

                    # Extra information (entity subtype + tags)
                    if ent.extra_information:
                        for extra in ent.extra_information:
                            if isinstance(extra, EntitySubtype):
                                print(f"    - [EntitySubtype] Value: {extra.value}")
                                for tag in extra.tags or []:
                                    tag = cast(EntityTag, tag)
                                    print(f"      • Tag: {tag.name}, Confidence: {tag.confidence_score}")
            print()

            # Global entities
            print("Global Entities:")
            for ent in conversation.entities or []:
                ent = cast(ConversationalAIEntity, ent)
                print(f"  Name: {ent.name}")
                print(f"  Text: {ent.text}")
                print(f"  Confidence: {ent.confidence_score}")
                print(f"  Offset: {ent.offset}, Length: {ent.length}")
                print(f"  Conversation Item ID: {ent.conversation_item_id}, " f"Index: {ent.conversation_item_index}")

                if ent.extra_information:
                    for extra in ent.extra_information:
                        if isinstance(extra, EntitySubtype):
                            print(f"    - [EntitySubtype] Value: {extra.value}")
                            for tag in extra.tags or []:
                                tag = cast(EntityTag, tag)
                                print(f"      • Tag: {tag.name}, Confidence: {tag.confidence_score}")
            print("-" * 40)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(sample_conversation_multi_turn_prediction_async())
# [END conversation_multi_turn_prediction_async]
