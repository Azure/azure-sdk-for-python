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
    ConversationAnalysisInput,
    ConversationAnalysisResult,
    QuestionAnsweringParameters
)
from azure.ai.language.questionanswering.models import KnowledgeBaseQueryOptions


class WorkflowDirectAnalysisTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_direct_kb_analysis(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="How do you make sushi rice?",
            direct_target="SushiMaking",
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    project_parameters={
                        "question": "How do you make sushi rice?",
                        "top": 1,
                        "confidenceScoreThreshold": 0.1
                    }
                )
            }
        )

        async with client:
            result = await client.analyze_conversations(
                params,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == "How do you make sushi rice?"

    @GlobalConversationAccountPreparer()
    async def test_direct_kb_analysis_with_model(self, conv_account, conv_key, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="How do you make sushi rice?",
            direct_target="SushiMaking",
            parameters={
                "SushiMaking": QuestionAnsweringParameters(
                    project_parameters=KnowledgeBaseQueryOptions(
                        question="How do you make sushi rice?",
                        top=1,
                        confidence_score_threshold=0.1
                    )
                )
            }
        )

        async with client:
            result = await client.analyze_conversations(
                params,
                project_name=workflow_project,
                deployment_name='production',
            )
        
        assert isinstance(result, ConversationAnalysisResult)
        assert result.query == "How do you make sushi rice?"
