# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.core.credentials import AzureKeyCredential
from testcase import GlobalConversationAccountPreparer
from asynctestcase import AsyncConversationTest
from azure.ai.language.conversations.aio import ConversationAnalysisClient


class OrchestrationAppQnaResponseAsyncTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_orchestration_app_qna_response(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        async with client:
            query = "How are you?"
            result = await client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "en",
                            "text": query
                        },
                        "isLoggingEnabled": False
                    },
                    "parameters": {
                        "projectName": orch_project_name,
                        "deploymentName": orch_deployment_name,
                        "verbose": True
                    }
                }
            )

            # assert - main object
            top_project = 'ChitChat-QnA'
            assert not result is None
            assert result["kind"] == "ConversationResult"
            assert result["result"]["query"] == query
            
            # assert - prediction type
            assert result["result"]["prediction"]["projectKind"] == "Orchestration"
            
            # assert - top matching project
            assert result["result"]["prediction"]["topIntent"] == top_project
            top_intent_object = result["result"]["prediction"]["intents"][top_project]
            assert top_intent_object["targetProjectKind"] == "QuestionAnswering"
            
            # assert intent and entities
            qna_result = top_intent_object["result"]
            answer = qna_result["answers"][0]["answer"]
            assert not answer is None
            assert qna_result["answers"][0]["confidenceScore"] >= 0
