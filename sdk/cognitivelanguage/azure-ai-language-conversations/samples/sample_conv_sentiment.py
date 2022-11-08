# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conv_sentiment.py

DESCRIPTION:
    This sample demonstrates how to analyze a conversation for sentiment analysis.

    For more info about how to setup a CLU conversation project, see the README.

USAGE:
    python sample_conv_sentiment.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONVERSATIONS_ENDPOINT                       - endpoint for your CLU resource.
    2) AZURE_CONVERSATIONS_KEY                            - API key for your CLU resource.
"""

def sample_conv_sentiment():
    # [START analyze_conversation_app]
    # import libraries
    import os
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.language.conversations import ConversationAnalysisClient

    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]

    # analyze quey
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    with client:

        poller = client.begin_conversation_analysis(
            task={
                "displayName": "Analyze PII in conversation",
                "analysisInput": {
                    "conversations": [
                        {
                            "conversationItems": [
                                {
                                    "id": "1",
                                    "participantId": "Customer",
                                    "modality": "transcript",
                                    "text": "My cat doesn't like the food, Can I get a refund?",
                                    "lexical": "my cat doesn't like the food can i get a refund"
                                },
                                {
                                    "id": "2",
                                    "participantId": "Agent",
                                    "modality": "transcript",
                                    "text": "Sure.You have been refunded. Have a nice day.",
                                    "lexical": "sure you have been refunded have a nice day"
                                },
                                {
                                    "id": "3",
                                    "participantId": "Customer",
                                    "modality": "transcript",
                                    "text": "Thanks for your help",
                                    "lexical": "thanks for your help"
                                }
                            ],
                            "modality": "transcript",
                            "id": "conversation1",
                            "language": "en"
                        }
                    ]
                },
                "tasks": [
                    {
                        "kind": "ConversationalSentimentTask",
                        "parameters": {
                            "modelVersion": "2022-10-01-preview",
                            "predictionSource": "text",
                        }
                    }
                ]
            }
        )

        # view result
        result = poller.result()
        task_result = result["tasks"]["items"][0]
        print("... view task status ...")
        print(f"status: {task_result['status']}")
        conv_sentiment_result = task_result["results"]
        if conv_sentiment_result["errors"]:
            print("... errors occurred ...")
            for error in conv_sentiment_result["errors"]:
                print(error)
        else:
            conversation_result = conv_sentiment_result["conversations"][0]
            if conversation_result["warnings"]:
                print("... view warnings ...")
                for warning in conversation_result["warnings"]:
                    print(warning)
            else:
                print("... view task result ...")
                for conversationItem in conversation_result["conversationItems"]:
                    confidenceScore=conversationItem['confidenceScores']
                    print(f"id: {conversationItem['id']}")
                    print(f"participantId: {conversationItem['participantId']}")
                    print(f"sentiment: {conversationItem['sentiment']}")
                    print(f"confidenceScores: positive={confidenceScore['positive']}  neutral={confidenceScore['neutral']}  negative={confidenceScore['negative']}")

    # [END analyze_conversation_app]


if __name__ == '__main__':
    sample_conv_sentiment()
