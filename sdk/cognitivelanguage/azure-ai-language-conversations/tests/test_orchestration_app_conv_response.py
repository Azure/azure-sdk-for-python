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
from azure.ai.language.conversations.models import (
    AnalyzeConversationResult,
    ConversationTargetIntentResult,
    OrchestratorPrediction,
)

class OrchestrationAppTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_orchestration_app(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = client.conversation_analysis.analyze_conversation(
                body={
                    "kind": "CustomConversation",
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
            assert isinstance(result, AnalyzeConversationResult)
            assert result.results.query == query
            # assert - prediction type
            assert isinstance(result.results.prediction, OrchestratorPrediction)
            assert result.results.prediction.project_kind == "workflow"
            # assert - top matching project
            assert result.results.prediction.top_intent == top_project
            top_intent_object = result.results.prediction.intents[top_project]
            assert isinstance(top_intent_object, ConversationTargetIntentResult)
            assert top_intent_object.target_kind == "conversation"
            # assert intent and entities
            conversation_result = top_intent_object.result.prediction
            assert conversation_result.top_intent == 'SendEmail'
            assert len(conversation_result.intents) > 0
            assert conversation_result.intents[0].category == 'SendEmail'
            assert conversation_result.intents[0].confidence_score > 0
            # assert - entities
            assert len(conversation_result.entities) > 0
            assert conversation_result.entities[0].category == 'ContactName'
            assert conversation_result.entities[0].text == 'Carol'
            assert conversation_result.entities[0].confidence_score > 0

