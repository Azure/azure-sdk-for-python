# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_orchestration_prediction.py

DESCRIPTION:
    This sample demonstrates how to analyze an utterance using an Orchestration project. 

USAGE:
    python sample_orchestration_prediction.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
    3) AZURE_CONVERSATIONS_PROJECT_NAME     - project name for your CLU conversations project.
    4) AZURE_CONVERSATIONS_DEPLOYMENT_NAME  - deployment name for your CLU conversations project.
"""


def sample_orchestration_prediction():
    # [START orchestration_prediction]
    # import libraries
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

    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    # analyze quey
    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
    # Build request
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

    response: AnalyzeConversationActionResult = client.analyze_conversation(data)

    conversation_result = cast(ConversationActionResult, response)
    prediction = conversation_result.result.prediction

    assert isinstance(prediction, OrchestrationPrediction)

    assert prediction.top_intent is not None, "top_intent missing in orchestration prediction"
    responding_project_name = cast(str, prediction.top_intent)
    print(f"Top intent: {responding_project_name}")

    target_intent_result = prediction.intents[responding_project_name]
    assert isinstance(target_intent_result, QuestionAnsweringTargetIntentResult)

    qa = target_intent_result.result
    for ans in qa.answers:
        print(ans.answer or "")

    # Final assertions like in C#
    assert responding_project_name == "ChitChat-QnA"


    # [END orchestration_prediction]


if __name__ == "__main__":
    sample_orchestration_prediction()
