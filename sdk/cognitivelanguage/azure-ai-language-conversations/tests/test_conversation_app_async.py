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
            assert result["result"]["prediction"]["topIntent"] == 'Send'
            assert len(result["result"]["prediction"]["intents"]) > 0
            assert result["result"]["prediction"]["intents"][0]["category"] == 'Send'
            assert result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0
            
            # assert - entities
            assert len(result["result"]["prediction"]["entities"]) > 0
            assert result["result"]["prediction"]["entities"][0]["category"] == 'Contact'
            assert result["result"]["prediction"]["entities"][0]["text"] == 'Carol'
            assert result["result"]["prediction"]["entities"][0]["confidenceScore"] > 0

    @pytest.mark.live_test_only
    @GlobalConversationAccountPreparer()
    async def test_conversation_app_aad_auth(self, endpoint, conv_project_name, conv_deployment_name):
        token = self.get_credential(ConversationAnalysisClient, is_async=True)
        client = ConversationAnalysisClient(endpoint, token, api_version="2022-05-01")
        async with client:
            query = "Send an email to Carol about the tomorrow's demo"
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
            assert result["result"]["prediction"]["topIntent"] == 'Send'
            assert len(result["result"]["prediction"]["intents"]) > 0
            assert result["result"]["prediction"]["intents"][0]["category"] == 'Send'
            assert result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0

            # assert - entities
            assert len(result["result"]["prediction"]["entities"]) > 0
            assert result["result"]["prediction"]["entities"][0]["category"] == 'Contact'
            assert result["result"]["prediction"]["entities"][0]["text"] == 'Carol'
            assert result["result"]["prediction"]["entities"][0]["confidenceScore"] > 0