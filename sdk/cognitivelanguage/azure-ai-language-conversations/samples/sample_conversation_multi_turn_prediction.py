# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_multi_turn_prediction.py

DESCRIPTION:
    Run a multi-turn conversation prediction synchronously using the
    Conversational AI task. Prints intents and entities, including spans,
    datetime resolutions, and subtype/tag metadata.

USAGE:
    python sample_conversation_multi_turn_prediction.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME
    
NOTE:
    If you prefer `AzureKeyCredential`, set:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
"""

# [START conversation_multi_turn_prediction]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationalAITask,
    ConversationalAIAnalysisInput,
    ConversationalAIActionContent,
    TextConversation,
    TextConversationItem,
    StringIndexType,
    ConversationalAITaskResult,
    DateTimeResolution,
    EntitySubtype,
    EntityTag,
)


def sample_conversation_multi_turn_prediction():
    # get settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # AAD credential
    credential = DefaultAzureCredential()

    client = ConversationAnalysisClient(endpoint, credential=credential)

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

    # Sync call
    response = client.analyze_conversation(data)

    if isinstance(response, ConversationalAITaskResult):
        ai_result = response.result
        if not ai_result or not ai_result.conversations:
            print("No conversations found in result.")
            return

        for conversation in ai_result.conversations or []:
            print(f"Conversation ID: {conversation.id}\n")

            # Intents
            print("Intents:")
            for intent in conversation.intents or []:
                print(f"  Name: {intent.name}")
                print(f"  Type: {intent.type}")

                print("  Conversation Item Ranges:")
                for rng in intent.conversation_item_ranges or []:
                    print(f"    - Offset: {rng.offset}, Count: {rng.count}")

                print("\n  Entities (Scoped to Intent):")
                for ent in intent.entities or []:
                    print(f"    Name: {ent.name}")
                    print(f"    Text: {ent.text}")
                    print(f"    Confidence: {ent.confidence_score}")
                    print(f"    Offset: {ent.offset}, Length: {ent.length}")
                    print(
                        f"    Conversation Item ID: {ent.conversation_item_id}, "
                        f"Index: {ent.conversation_item_index}"
                    )

                    # Date/time resolutions
                    for res in ent.resolutions or []:
                        if isinstance(res, DateTimeResolution):
                            print(
                                f"    - [DateTimeResolution] SubKind: {res.date_time_sub_kind}, "
                                f"Timex: {res.timex}, Value: {res.value}"
                            )

                    # Extra information (entity subtype + tags)
                    for extra in ent.extra_information or []:
                        if isinstance(extra, EntitySubtype):
                            print(f"    - [EntitySubtype] Value: {extra.value}")
                            for tag in extra.tags or []:
                                print(f"      • Tag: {tag.name}, Confidence: {tag.confidence_score}")
                print()

                # Global entities
                print("Global Entities:")
                for ent in conversation.entities or []:
                    print(f"  Name: {ent.name}")
                    print(f"  Text: {ent.text}")
                    print(f"  Confidence: {ent.confidence_score}")
                    print(f"  Offset: {ent.offset}, Length: {ent.length}")
                    print(
                        f"  Conversation Item ID: {ent.conversation_item_id}, " f"Index: {ent.conversation_item_index}"
                    )

                    for extra in ent.extra_information or []:
                        if isinstance(extra, EntitySubtype):
                            print(f"    - [EntitySubtype] Value: {extra.value}")
                            for tag in extra.tags or []:
                                print(f"      • Tag: {tag.name}, Confidence: {tag.confidence_score}")
                print("-" * 40)
    else:
        print("No Conversational AI result returned.")


# [END conversation_multi_turn_prediction]


def main():
    sample_conversation_multi_turn_prediction()


if __name__ == "__main__":
    main()
