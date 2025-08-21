# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_prediction_with_options.py

DESCRIPTION:
    This sample demonstrates how to analyze an utterance using a CLU Conversation project,
    showing how to set additional options such as `verbose=True`.

USAGE:
    python sample_conversation_prediction_with_options.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME
"""

# [START conversation_prediction_with_options]
import os
from typing import cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationLanguageUnderstandingInput,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionContent,
    StringIndexType,
    AnalyzeConversationActionResult,
    ConversationActionResult,
    ConversationPrediction,
    DateTimeResolution,
)


def sample_conversation_prediction_with_options():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # create client
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

    # build request with `verbose=True`
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

    # analyze utterance
    response: AnalyzeConversationActionResult = client.analyze_conversation(data)

    # cast to conversation result
    conversation_result = cast(ConversationActionResult, response)
    prediction = cast(ConversationPrediction, conversation_result.result.prediction)

    # print top intent
    print(f"Top intent: {prediction.top_intent}\n")

    # print intents
    print("Intents:")
    for intent in prediction.intents:
        print(f"  Category: {intent.category}")
        print(f"  Confidence: {intent.confidence}")
        print()

    # print entities
    print("Entities:")
    for entity in prediction.entities:
        print(f"  Category: {entity.category}")
        print(f"  Text: {entity.text}")
        print(f"  Offset: {entity.offset}")
        print(f"  Length: {entity.length}")
        print(f"  Confidence: {entity.confidence}")

        if entity.resolutions:
            for res in entity.resolutions:
                if isinstance(res, DateTimeResolution):
                    print("  DateTime Resolution:")
                    print(f"    Sub Kind: {res.date_time_sub_kind}")
                    print(f"    Timex: {res.timex}")
                    print(f"    Value: {res.value}")
        print()

    # optional assertion for consistency
    assert prediction.top_intent == "SendEmail"


if __name__ == "__main__":
    sample_conversation_prediction_with_options()
# [END conversation_prediction_with_options]
