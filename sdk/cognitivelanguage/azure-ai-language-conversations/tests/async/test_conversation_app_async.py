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


class ConversationAppAsyncTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_conversation_app(self, endpoint, key, conv_project_name, conv_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        async with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = await client.conversation_analysis.analyze_conversation(
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
                        "projectName": conv_project_name,
                        "deploymentName": conv_deployment_name,
                        "verbose": True
                    }
                }
            )
        
            # assert - main object
            assert not result is None
            assert result["kind"] == "ConversationResult"
            
            # assert - prediction type
            assert result["result"]["query"] == query
            assert result["result"]["prediction"]["projectKind"] == 'Conversation'
            
            # assert - top intent
            assert result["result"]["prediction"]["topIntent"] == 'Read'
            assert len(result["result"]["prediction"]["intents"]) > 0
            assert result["result"]["prediction"]["intents"][0]["category"] == 'Read'
            assert result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0
            
            # assert - entities
            assert len(result["result"]["prediction"]["entities"]) > 0
            assert result["result"]["prediction"]["entities"][0]["category"] == 'Contact'
            assert result["result"]["prediction"]["entities"][0]["text"] == 'Carol'
            assert result["result"]["prediction"]["entities"][0]["confidenceScore"] > 0
