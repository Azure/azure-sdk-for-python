# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import (
    ConversationTest,
    GlobalConversationAccountPreparer
)
from azure.ai.language.conversations import ConversationAnalysisClient


class TestConversationalPiiTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_conversational_pii(self, endpoint, key):
        # analyze query
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
                                        "participantId": "0",
                                        "modality": "transcript",
                                        "text": "It is john doe.",
                                        "lexical": "It is john doe",
                                        "itn": "It is john doe",
                                        "maskedItn": "It is john doe"
                                    },
                                    {
                                        "id": "2",
                                        "participantId": "1",
                                        "modality": "transcript",
                                        "text": "Yes, 633-27-8199 is my phone",
                                        "lexical": "yes six three three two seven eight one nine nine is my phone",
                                        "itn": "yes 633278199 is my phone",
                                        "maskedItn": "yes 633278199 is my phone",
                                    },
                                    {
                                        "id": "3",
                                        "participantId": "1",
                                        "modality": "transcript",
                                        "text": "j.doe@yahoo.com is my email",
                                        "lexical": "j dot doe at yahoo dot com is my email",
                                        "maskedItn": "j.doe@yahoo.com is my email",
                                        "itn": "j.doe@yahoo.com is my email",
                                    }
                                ],
                                "modality": "transcript",
                                "id": "1",
                                "language": "en"
                            }
                        ]
                    },
                    "tasks": [
                        {
                            "kind": "ConversationalPIITask",
                            "parameters": {
                                "redactionSource": "lexical",
                                "piiCategories": [
                                    "all"
                                ]
                            }
                        }
                    ]
                }
            )

            # assert - main object
            result = poller.result()
            assert not result is None
            assert result["status"] == "succeeded"

            # assert - task result
            task_result = result["tasks"]["items"][0]
            assert task_result["status"] == "succeeded"
            assert task_result["kind"] == "conversationalPIIResults"

            # assert - conv result
            conversation_items = task_result["results"]["conversations"][0]["conversationItems"]
            assert not conversation_items is None
            for conversation in conversation_items:
                assert not conversation["redactedContent"] is None
                assert not conversation["entities"] is None
