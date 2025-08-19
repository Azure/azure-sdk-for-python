# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_prediction_with_language.py

DESCRIPTION:
    This sample demonstrates how to analyze an utterance in a non-English language
    (Spanish in this example) using a CLU Conversation project.

USAGE:
    python sample_conversation_prediction_with_language.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME
"""

# [START conversation_prediction_with_language]
import os
from typing import cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationLanguageUnderstandingInput,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationLanguageUnderstandingActionContent,
    StringIndexType,
    AnalyzeConversationActionResult,
    ConversationActionResult,
    ConversationPrediction,
    DateTimeResolution,
)


def sample_conversation_prediction_with_language():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # create client
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

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
        action_content=ConversationLanguageUnderstandingActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
            verbose=True,
        ),
    )

    # call the service
    response: AnalyzeConversationActionResult = client.analyze_conversation(data)

    # cast to conversation result
    conversation_result = cast(ConversationActionResult, response)
    prediction = conversation_result.result.prediction
    assert isinstance(prediction, ConversationPrediction)

    # print top intent
    print(f"Top intent: {prediction.top_intent}\n")

    # print intents
    print("Intents:")
    for intent in prediction.intents or []:
        print(f"  Category: {intent.category}")
        print(f"  Confidence: {intent.confidence}")
        print()

    # print entities
    print("Entities:")
    for entity in prediction.entities or []:
        print(f"  Category: {entity.category}")
        print(f"  Text: {entity.text}")
        print(f"  Offset: {entity.offset}")
        print(f"  Length: {entity.length}")
        print(f"  Confidence: {entity.confidence}")

        if entity.resolutions:
            for res in entity.resolutions:
                if isinstance(res, DateTimeResolution):
                    print("  DateTime Resolution:")
                    print(f"    Sub Kind: {getattr(res, 'date_time_sub_kind', None)}")
                    print(f"    Timex: {res.timex}")
                    print(f"    Value: {res.value}")
        print()

    # optional final assertion
    assert prediction.top_intent == "SendEmail"


if __name__ == "__main__":
    sample_conversation_prediction_with_language()
# [END conversation_prediction_with_language]