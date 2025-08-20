# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_orchestration_prediction.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration project.
    In this sample, orchestration project's top intent will map to a Qna project.

    For more info about how to setup a CLU orchestration project, see the README.

USAGE:
    python sample_orchestration_prediction.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
    AZURE_CONVERSATIONS_PROJECT_NAME
    AZURE_CONVERSATIONS_DEPLOYMENT_NAME
"""

# [START orchestration_prediction]
import os
from typing import cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    AnalyzeConversationActionResult,
    ConversationLanguageUnderstandingActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    StringIndexType,
    ConversationLanguageUnderstandingInput,
    OrchestrationPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationActionResult,
)


def sample_orchestration_prediction():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # create client
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

    # build request using strongly-typed models
    data = ConversationLanguageUnderstandingInput(
        conversation_input=ConversationAnalysisInput(
            conversation_item=TextConversationItem(
                id="1",
                participant_id="participant1",
                text="How are you?",
            )
        ),
        action_content=ConversationLanguageUnderstandingActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
        ),
    )

    # call the service
    response: AnalyzeConversationActionResult = client.analyze_conversation(data)

    # cast to the orchestration result type
    conversation_result = cast(ConversationActionResult, response)
    prediction = conversation_result.result.prediction

    assert isinstance(prediction, OrchestrationPrediction)

    # ensure a top intent was returned
    assert prediction.top_intent is not None, "top_intent missing in orchestration prediction"
    responding_project_name = cast(str, prediction.top_intent)
    print(f"Top intent: {responding_project_name}")

    # get the routed target result
    target_intent_result = prediction.intents[responding_project_name]
    assert isinstance(target_intent_result, QuestionAnsweringTargetIntentResult)

    # print answers from the QnA result
    qa = target_intent_result.result
    for ans in qa.answers: # type: ignore
        print(ans.answer or "")

    # optional final assertion
    assert responding_project_name == "ChitChat-QnA"


if __name__ == "__main__":
    sample_orchestration_prediction()
# [END orchestration_prediction]
