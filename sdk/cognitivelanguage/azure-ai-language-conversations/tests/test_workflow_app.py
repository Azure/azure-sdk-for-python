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
    ConversationAnalysisInput,
    ConversationAnalysisResult,
    QuestionAnsweringParameters,
    DeepstackParameters,
    DeepstackCallingOptions,
    QuestionAnsweringTargetIntentResult,
    WorkflowPrediction,
    DSTargetIntentResult
)
from azure.ai.language.questionanswering.models import KnowledgeBaseQueryOptions


class WorkflowAppTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_workflow_app(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:

            # analyze query
            query = "How do you make sushi rice?"
            result = client.analyze_conversations(
                {"query": query},
                project_name=workflow_project,
                deployment_name='production',
            )
        
            # assert
            assert isinstance(result, ConversationAnalysisResult)
            assert result.query == query
            assert isinstance(result.prediction, WorkflowPrediction)
            assert result.prediction.project_kind == "workflow"
            assert result.prediction.top_intent == "SushiMaking"
            assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)

            # analyze query
            query = "I will have sashimi"
            result = client.analyze_conversations(
                {"query": query},
                project_name=workflow_project,
                deployment_name='production',
            )
        
            # assert
            assert isinstance(result, ConversationAnalysisResult)
            assert result.query == query
            assert isinstance(result.prediction, WorkflowPrediction)
            assert result.prediction.project_kind == "workflow"
            assert result.prediction.top_intent == "SushiOrder"
            assert isinstance(result.prediction.intents, DSTargetIntentResult)


    @GlobalConversationAccountPreparer()
    def test_workflow_app_with_parameters(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "How do you make sushi rice?",
        input = ConversationAnalysisInput(
            query=query,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    calling_options={
                        "question": query,
                        "top": 1,
                        "confidenceScoreThreshold": 0.1
                    }
                ),
                "SushiOrder": DeepstackParameters(
                    calling_options={
                        "verbose": True
                    }
                )
            }
        )

        # run quey
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                input,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == "SushiMaking"
        assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)


    @GlobalConversationAccountPreparer()
    def test_workflow_app_with_model(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "How do you make sushi rice?"
        input = ConversationAnalysisInput(
            query=query,
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    calling_options=KnowledgeBaseQueryOptions(
                        question=query,
                        top=1,
                        confidence_score_threshold=0.1
                    )
                ),
                "SushiOrder": DeepstackParameters(
                    calling_options=DeepstackCallingOptions(
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
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == "SushiMaking"
        assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)
