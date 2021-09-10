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
    DeepstackCallingOptions
)
from azure.ai.language.questionanswering.models import KnowledgeBaseQueryOptions


class WorkflowDirectAnalysisTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_workflow_analysis(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                {"query": "How do you make sushi rice?"},
                project_name=workflow_project,
                deployment_name='production',
            )
        
            assert isinstance(result, ConversationAnalysisResult)
            assert result.query == "How do you make sushi rice?"
            assert result.prediction.top_intent == "SushiMaking"

            result = client.analyze_conversations(
                {"query": "I will have sashimi"},
                project_name=workflow_project,
                deployment_name='production',
            )
        
            assert isinstance(result, ConversationAnalysisResult)
            assert result.query == "I will have sashimi"

    @GlobalConversationAccountPreparer()
    def test_workflow_analysis_with_parameters(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="How do you make sushi rice?",
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    project_parameters={
                        "question": "How do you make sushi rice?",
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

        with client:
            result = client.analyze_conversations(
                params,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == "How do you make sushi rice?"

    @GlobalConversationAccountPreparer()
    def test_workflow_analysis_with_model(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="How do you make sushi rice?",
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    project_parameters=KnowledgeBaseQueryOptions(
                        question="How do you make sushi rice?",
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

        with client:
            result = client.analyze_conversations(
                params,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == "How do you make sushi rice?"
