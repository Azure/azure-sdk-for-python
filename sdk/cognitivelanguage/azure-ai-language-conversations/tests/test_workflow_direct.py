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
    QuestionAnsweringParameters
)


class WorkflowDirectAnalysisTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_direct_analysis(self, conv_account, conv_key, qna_project, workflow_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="What is in sushi rice?",
            direct_target=qna_project,
            parameters={
                qna_project: QuestionAnsweringParameters(
                    target_type="question_answering",
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
        assert result.query == "What is in sushi rice?"
