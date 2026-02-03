# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_prediction_with_language_async.py

DESCRIPTION:
    This sample demonstrates how to analyze an utterance in a non-English language
    (Spanish in this example) using a CLU Conversation project (async).

USAGE:
    python sample_conversation_prediction_with_language_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_ENDPOINT
      - AZURE_CONVERSATIONS_KEY
"""

# [START conversation_prediction_with_language_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationLanguageUnderstandingInput,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionContent,
    StringIndexType,
    ConversationActionResult,
    ConversationPrediction,
    DateTimeResolution,
)


async def sample_conv_prediction_language_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    credential = DefaultAzureCredential()

    async with ConversationAnalysisClient(endpoint, credential=credential) as client:
        # build request with Spanish input text
        data = ConversationLanguageUnderstandingInput(
            conversation_input=ConversationAnalysisInput(
                conversation_item=TextConversationItem(
                    id="1",
                    participant_id="participant1",
                    text="Enviar un email a Carol acerca de la presentación de mañana",
                    language="es",  # specify input language
                )
            ),
            action_content=ConversationActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
                verbose=True,
            ),
        )

        # call async API
        response = await client.analyze_conversation(data)

        if isinstance(response, ConversationActionResult):
            pred = response.result.prediction
            if isinstance(pred, ConversationPrediction):
                # top intent
                print(f"Top intent: {pred.top_intent}\n")

                # intents
                print("Intents:")
                for intent in pred.intents or []:
                    print(f"  Category: {intent.category}")
                    print(f"  Confidence: {intent.confidence}")
                    print()

                # entities
                print("Entities:")
                for entity in pred.entities or []:
                    print(f"  Category: {entity.category}")
                    print(f"  Text: {entity.text}")
                    print(f"  Offset: {entity.offset}")
                    print(f"  Length: {entity.length}")
                    print(f"  Confidence: {entity.confidence}")

                    for res in entity.resolutions or []:
                        if isinstance(res, DateTimeResolution):
                            print("  DateTime Resolution:")
                            print(f"    Sub Kind: {res.date_time_sub_kind}")
                            print(f"    Timex: {res.timex}")
                            print(f"    Value: {res.value}")
                    print()
        else:
            print("Unexpected result type from analyze_conversation.")


# [END conversation_prediction_with_language_async]


async def main():
    await sample_conv_prediction_language_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
