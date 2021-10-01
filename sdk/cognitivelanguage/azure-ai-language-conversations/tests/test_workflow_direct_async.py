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
from azure.ai.language.conversations.models import (
    AnalyzeConversationOptions,
    AnalyzeConversationResult,
    QuestionAnsweringParameters,
    DeepstackParameters,
    WorkflowPrediction,
    QuestionAnsweringTargetIntentResult,
    DSTargetIntentResult,
    LUISTargetIntentResult
)

class WorkflowAppDirectAsyncTests(AsyncConversationTest):

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    async def test_direct_kb_intent(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "How do you make sushi rice?"
        target_intent = "SushiMaking"
        input = AnalyzeConversationOptions(
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
        async with client:
            result = await client.analyze_conversations(
                input,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        # assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    async def test_kb_intent_with_model(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "How do you make sushi rice?"
        target_intent = "SushiMaking"
        input = AnalyzeConversationOptions(
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
        async with client:
            result = await client.analyze_conversations(
                input,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        # assert isinstance(result.prediction.intents, QuestionAnsweringTargetIntentResult)

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    async def test_deepstack_intent(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "I will have the oyako donburi please."
        target_intent = "SushiOrder"
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        input = AnalyzeConversationOptions(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiOrder": DeepstackParameters(
                    calling_options={
                       "verbose": True,
                    }
                )
            }
        )

        # analyze query
        async with client:
            result = await client.analyze_conversations(
                input,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        # assert isinstance(result.prediction.intents, DSTargetIntentResult)

    @pytest.mark.skip(reason="internal server error!")
    @GlobalConversationAccountPreparer()
    async def test_luis_intent(self, conv_account, conv_key, workflow_project):

        # prepare data
        query = "I will have the oyako donburi please."
        target_intent = "SushiOrder"
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        input = AnalyzeConversationOptions(
            query=query,
            direct_target=target_intent,
            parameters={
                "SushiOrder": DeepstackParameters(
                    calling_options={
                       "verbose": True,
                    }
                )
            }
        )

        # analyze query
        async with client:
            result = await client.analyze_conversations(
                input,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        assert isinstance(result.prediction, WorkflowPrediction)
        assert result.prediction.project_kind == "workflow"
        assert result.prediction.top_intent == target_intent
        # assert isinstance(result.prediction.intents, LUISTargetIntentResult)