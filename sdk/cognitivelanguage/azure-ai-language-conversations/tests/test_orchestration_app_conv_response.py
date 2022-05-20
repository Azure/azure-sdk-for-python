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

class OrchestrationAppConvResponseTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_orchestration_app_conv_response(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = client.analyze_conversation(
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
            top_project = "EmailIntent"
            assert not result is None
            assert result["kind"] == "ConversationResult"
            assert result["result"]["query"] == query
            
            # assert - prediction type
            assert result["result"]["prediction"]["projectKind"] == "Orchestration"
            
            # assert - top matching project
            assert result["result"]["prediction"]["topIntent"] == top_project
            top_intent_object = result["result"]["prediction"]["intents"][top_project]
            assert top_intent_object["targetProjectKind"] == "Conversation"
            
            # assert intent and entities
            conversation_result = top_intent_object["result"]["prediction"]
            assert conversation_result["topIntent"] == 'Read'
            assert len(conversation_result["intents"]) > 0
            assert conversation_result["intents"][0]["category"] == 'Read'
            assert conversation_result["intents"][0]["confidenceScore"] > 0
            
            # assert - entities
            assert len(conversation_result["entities"]) > 0
            assert conversation_result["entities"][0]["category"] == 'Contact'
            assert conversation_result["entities"][0]["text"] == 'Carol'
            assert conversation_result["entities"][0]["confidenceScore"] > 0

