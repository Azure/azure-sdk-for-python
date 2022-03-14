# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_orchestration_app_conversation_response.py

DESCRIPTION:
    This sample demonstrates how to analyze user query using an orchestration project.
    In this sample, orchestration project's top intent will map to a conversation project.

    For more info about how to setup a CLU orchestration project, see the README.

USAGE:
    python sample_analyze_orchestration_app_conversation_response.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your CLU resource.
    2) AZURE_CONVERSATIONS_KEY - your CLU API key.
    3) AZURE_CONVERSATIONS_WORKFLOW_PROJECT - the name of your CLU orchestration project.
"""

def sample_analyze_orchestration_app_conversation_response():
    # [START analyze_orchestration_app_conversation_response]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import ConversationAnalysisOptions

    # get secrets
    conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    orchestration_project = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT"]

    # analyze query
    client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
    with client:
        result = client.conversation_analysis.analyze_conversation(
            body={
                "kind": "CustomConversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "en",
                        "text": "book a flight on Monday 1/1/2022 from London to Seattle"
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": orchestration_project,
                    "deploymentName": "production",
                    "verbose": True
                }
            }
        )

    # view result
    print("query: {}".format(result.results.query))
    print("project kind: {}".format(result.results.prediction.project_kind))

    # top intent
    top_intent = result.results.prediction.top_intent
    print("top intent: {}".format(top_intent))
    top_intent_object = result.results.prediction.intents[top_intent]
    print("confidence score: {}".format(top_intent_object.confidence))

    # conversation result
    print("view conversation result:")
    print("intents:")
    for intent in top_intent_object.result.results.prediction.intents:
        print("category: {}".format(intent.category))
        print("confidence score: {}".format(intent.confidence_score))

    print("view entities:")
    for entity in top_intent_object.result.results.prediction.entities:
        print("category: {}".format(entity.category))
        print("text: {}".format(entity.text))
        print("confidence score: {}".format(entity.confidence_score))

    # [END analyze_orchestration_app_conversation_response]

if __name__ == '__main__':
    sample_analyze_orchestration_app_conversation_response()