# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase


class TestConversationalSummarizationAsync(AzureRecordedTestCase):

    @pytest.mark.asyncio
    async def test_conversational_summarization(self, recorded_test, conversation_creds):
        # analyze query
        client = ConversationAnalysisClient(
            conversation_creds["endpoint"],
            AzureKeyCredential(conversation_creds["key"])
        )
        async with client:
            poller = await client.begin_conversation_analysis(
                task={
                    "displayName": "Analyze conversations from xxx",
                    "analysisInput": {
                        "conversations": [
                            {
                                "conversationItems": [
                                    {
                                        "text": "Hello, how can I help you?",
                                        "modality": "text",
                                        "id": "1",
                                        "participantId": "Agent"
                                    },
                                    {
                                        "text": "How to upgrade Office? I am getting error messages the whole day.",
                                        "modality": "text",
                                        "id": "2",
                                        "participantId": "Customer"
                                    },
                                    {
                                        "text": "Press the upgrade button please. Then sign in and follow the instructions.",
                                        "modality": "text",
                                        "id": "3",
                                        "participantId": "Agent"
                                    }
                                ],
                                "modality": "text",
                                "id": "conversation1",
                                "language": "en"
                            },
                        ]
                    },
                    "tasks": [
                        {
                            "taskName": "analyze 1",
                            "kind": "ConversationalSummarizationTask",
                            "parameters": {
                                "summaryAspects": ["Issue, Resolution"]
                            }
                        }
                    ]
                }
            )

            # assert - main object
            result = await poller.result()
            assert not result is None
            assert result["status"] == "succeeded"

            # assert - task result
            task_result = result["tasks"]["items"][0]
            assert task_result["status"] == "succeeded"
            assert task_result["kind"] == "conversationalSummarizationResults"

            # assert - conv result
            conversation_result = task_result["results"]["conversations"][0]
            summaries = conversation_result["summaries"]
            assert summaries is not None
