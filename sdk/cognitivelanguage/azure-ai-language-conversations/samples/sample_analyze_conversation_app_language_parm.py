# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_analyze_conversation_app_language_parm.py

DESCRIPTION:
    This sample demonstrates how to analyze user query for intents and entities using
    a conversation project with a language parameter.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_analyze_conversation_app_language_parm.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT - the endpoint to your CLU resource.
    2) AZURE_CONVERSATIONS_KEY - your CLU API key.
    3) AZURE_CONVERSATIONS_PROJECT - the name of your CLU conversations project.
"""

def sample_analyze_conversation_app_language_parm():
    # [START analyze_conversation_app_language_parm]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient
    from azure.ai.language.conversations.models import ConversationAnalysisOptions

    # get secrets
    conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
    conv_project = os.environ["AZURE_CONVERSATIONS_PROJECT"]

    # analyze quey
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
                    "projectName": conv_project,
                    "deploymentName": "production",
                    "verbose": True
                }
            }
        )

    # view result
    print("query: {}".format(result.results.query))
    print("project kind: {}\n".format(result.results.prediction.project_kind))

    print("view top intent:")
    print("top intent: {}".format(result.results.prediction.top_intent))
    print("category: {}".format(result.results.prediction.intents[0].category))
    print("confidence score: {}\n".format(result.results.prediction.intents[0].confidence))

    print("view entities:")
    for entity in result.results.prediction.entities:
        print("category: {}".format(entity.category))
        print("text: {}".format(entity.text))
        print("confidence score: {}".format(entity.confidence))
        if entity.resolutions:
            print("resolutions")
            for resolution in entity.resolutions:
                print("text: {}".format(resolution.text))
                print("kind: {}".format(resolution.resolution_kind))
                print("value: {}".format(resolution.value))

    # [END analyze_conversation_app_language_parm]


if __name__ == '__main__':
    sample_analyze_conversation_app_language_parm()
