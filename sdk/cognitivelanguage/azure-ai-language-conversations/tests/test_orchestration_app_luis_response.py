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

class OrchestrationAppLuisResponseTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_orchestration_app_luis_response(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            query = "Reserve a table for 2 at the Italian restaurant"
            result = client.conversation_analysis.analyze_conversation(
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
            top_project = "RestaurantIntent"
            assert not result is None
            assert result["kind"] == "ConversationResult"
            assert result["result"]["query"] == query
            
            # assert - prediction type
            assert result["result"]["prediction"]["projectKind"] == "Orchestration"
            
            # assert - top matching project
            assert result["result"]["prediction"]["topIntent"] == top_project
            top_intent_object = result["result"]["prediction"]["intents"][top_project]
            assert top_intent_object["targetProjectKind"] == "Luis"
            
            # assert intent and entities
            top_intent = "Reserve"
            luis_result = top_intent_object["result"]["prediction"]
            assert luis_result["topIntent"] == top_intent
            assert len(luis_result["intents"]) > 0
            assert luis_result["intents"][top_intent]["score"] > 0
            
            # assert - entities
            assert len(luis_result["entities"]) > 0

