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
    AnalysisParameters,
    AnalyzeConversationResult,
    QuestionAnsweringParameters,
    ConversationParameters,
    OrchestratorPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationTargetIntentResult,
    LUISTargetIntentResult
)


class OrchestrationAppDirectTests(ConversationTest):

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    def test_direct_kb_intent(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "How do you make sushi rice?"
        target_intent = "SushiMaking"
        input = AnalysisParameters(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    calling_options={
                        "question": query,
                        "top": 1,
                        "confidenceScoreThreshold": 0.1
                    }
                )
            }
        )

        # analyze query
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                input,
                project_name=orchestration_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    def test_kb_intent_with_model(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "How do you make sushi rice?"
        target_intent = "SushiMaking"
        input = AnalysisParameters(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    caling_options={
                        "question":query,
                        "top":1,
                        "confidence_score_threshold":0.1
                    }
                )
            }
        )

        # analyze query
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                input,
                project_name=orchestration_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    def test_conversation_intent(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "I will have the oyako donburi please."
        target_intent = "SushiOrder"
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        input = AnalysisParameters(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiOrder": ConversationParameters(
                    calling_options={
                       "verbose": True,
                    }
                )
            }
        )

        # analyze query
        with client:
            result = client.analyze_conversations(
                input,
                project_name=orchestration_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        assert isinstance(result.prediction.intents, ConversationTargetIntentResult)


    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    def test_luis_intent(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "I will have the oyako donburi please."
        target_intent = "SushiOrder"
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        input = AnalysisParameters(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiOrder": ConversationParameters(
                    calling_options={
                       "verbose": True,
                    }
                )
            }
        )

        # analyze query
        with client:
            result = client.analyze_conversations(
                input,
                project_name=orchestration_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        assert isinstance(result.prediction.intents, LUISTargetIntentResult)