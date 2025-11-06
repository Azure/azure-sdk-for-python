# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_orchestration_prediction.py

DESCRIPTION:
    This sample demonstrates how to analyze a user query using an orchestration project.
    In this sample, the orchestration project's top intent routes to a QnA project.

USAGE:
    python sample_orchestration_prediction.py

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
      - AZURE_CONVERSATIONS_PROJECT_NAME
      - AZURE_CONVERSATIONS_DEPLOYMENT_NAME
"""

# [START orchestration_prediction]
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    StringIndexType,
    ConversationLanguageUnderstandingInput,
    OrchestrationPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationActionResult,
)


def sample_orchestration_prediction():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    credential = DefaultAzureCredential()
    client = ConversationAnalysisClient(endpoint, credential=credential)

    # Build request using strongly-typed models
    data = ConversationLanguageUnderstandingInput(
        conversation_input=ConversationAnalysisInput(
            conversation_item=TextConversationItem(
                id="1",
                participant_id="participant1",
                text="How are you?",
            )
        ),
        action_content=ConversationActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
        ),
    )

    # Call sync API
    response = client.analyze_conversation(data)

    # Narrow to expected result types
    if isinstance(response, ConversationActionResult):
        pred = response.result.prediction
        if isinstance(pred, OrchestrationPrediction):
            # Top intent name is the routed project name
            top_intent = pred.top_intent
            if not top_intent:
                print("No top intent was returned by orchestration.")
                return

            print(f"Top intent (responding project): {top_intent}")

            # Look up the routed target result
            target_intent_result = pred.intents.get(top_intent)
            if not isinstance(target_intent_result, QuestionAnsweringTargetIntentResult):
                print("Top intent did not route to a Question Answering result.")
                return

            qa = target_intent_result.result
            if qa is not None and qa.answers is not None:
                for ans in qa.answers:
                    print(ans.answer or "")
        else:
            print("Prediction was not an OrchestrationPrediction.")
    else:
        print("Unexpected result type from analyze_conversation.")


# [END orchestration_prediction]


def main():
    sample_orchestration_prediction()


if __name__ == "__main__":
    main()
