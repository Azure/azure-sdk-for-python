# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase


class TestConversationalSentimentTask(AzureRecordedTestCase):

    def test_conversational_sentiment_task(self, recorded_test, conversation_creds):
        # analyze query
        client = ConversationAnalysisClient(
            conversation_creds["endpoint"],
            AzureKeyCredential(conversation_creds["key"])
        )
        with client:
            poller = client.begin_conversation_analysis(
                task={
                  "displayName": "Sentiment Analysis from a call center conversation",
                  "analysisInput": {
                    "conversations": [
                      {
                        "id": "1",
                        "language": "en",
                        "modality": "transcript",
                        "conversationItems": [
                          {
                            "participantId": "1",
                            "id": "1",
                            "text": "I like the service. I do not like the food",
                            "lexical": "i like the service i do not like the food",
                          }
                        ]
                      }
                    ]
                  },
                  "tasks": [
                    {
                      "taskName": "Conversation Sentiment Analysis",
                      "kind": "ConversationalSentimentTask",
                      "parameters": {
                        "modelVersion": "latest",
                        "predictionSource": "text"
                      }
                    }
                  ]
                }
            )

            # assert - main object
            result = poller.result()
            assert result is not None
            assert result["status"] == "succeeded"

            # assert - task result
            task_result = result["tasks"]["items"][0]
            assert task_result["status"] == "succeeded"
            # assert task_result["kind"] == "conversationalSentimentResults" https://dev.azure.com/msazure/Cognitive%20Services/_workitems/edit/16041272

            # assert - conv result
            sentiment_result = task_result["results"]["conversations"][0]
            conversation_sentiment = sentiment_result["conversationItems"][0]
            assert conversation_sentiment["sentiment"] == "mixed"
            assert conversation_sentiment["participantId"] == "1"
            assert conversation_sentiment["confidenceScores"]

