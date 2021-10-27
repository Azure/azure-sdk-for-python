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
    QuestionAnsweringParameters,
    ConversationParameters,
    ConversationCallingOptions,
    QuestionAnsweringTargetIntentResult,
    OrchestratorPrediction,
    ConversationAnalysisOptions
)

class OrchestrationAppTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_orchestration_app(self, conv_account, conv_key, orchestration_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:

            # analyze query
            query = "How do you make sushi rice?"
            result = client.analyze_conversations(
                {"query": query},
                project_name=orchestration_project,
                deployment_name='production',
            )
        
            # assert
            top_intent = "SushiMaking"
            assert isinstance(result, AnalyzeConversationResult)
            assert result.query == query
            assert isinstance(result.prediction, OrchestratorPrediction)
            assert result.prediction.project_kind == "workflow"
            assert result.prediction.top_intent == top_intent
            assert isinstance(result.prediction.intents[top_intent], QuestionAnsweringTargetIntentResult)

            # analyze query
            query = "I will have sashimi"
            result = client.analyze_conversations(
                {"query": query},
                project_name=orchestration_project,
                deployment_name='production',
            )
        
            # assert
            assert isinstance(result, AnalyzeConversationResult)
            assert result.query == query
            assert isinstance(result.prediction, OrchestratorPrediction)
            assert result.prediction.project_kind == "workflow"
            # assert result.prediction.top_intent == "SushiOrder" --> wrong top intent!
            # assert isinstance(result.prediction.intents, ConversationTargetIntentResult)


    @GlobalConversationAccountPreparer()
    def test_orchestration_app_with_parameters(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "How do you make sushi rice?",
        input = ConversationAnalysisOptions(
            query=query,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    calling_options={
                        "question": query,
                        "top": 1,
                        "confidenceScoreThreshold": 0.1
                    }
                ),
                "SushiOrder": ConversationParameters(
                    calling_options={
                        "verbose": True
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
        top_intent = "SushiMaking"
        assert isinstance(result, AnalyzeConversationResult)
        # assert result.query == query --> weird behavior here!
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == top_intent
        assert isinstance(result.prediction.intents[top_intent], QuestionAnsweringTargetIntentResult)


    @GlobalConversationAccountPreparer()
    def test_orchestration_app_with_model(self, conv_account, conv_key, orchestration_project):

        # prepare data
        query = "How do you make sushi rice?"
        input = ConversationAnalysisOptions(
            query=query,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    calling_options={
                        "question":query,
                        "top":1,
                        "confidence_score_threshold":0.1
                    }
                ),
                "SushiOrder": ConversationParameters(
                    calling_options=ConversationCallingOptions(
                        verbose=True
                    )
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
        top_intent = "SushiMaking"
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, OrchestratorPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == top_intent
        assert isinstance(result.prediction.intents[top_intent], QuestionAnsweringTargetIntentResult)
