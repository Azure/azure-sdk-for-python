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
    DeepstackParameters,
    LUISV2Parameters,
    LUISV3Parameters,
    QuestionAnsweringParameters,
)


class ConversationAnalysisTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_analysis(self, conv_account, conv_key, conv_project):

        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = ConversationAnalysisInput(
            query="One california maki please.",

            #direct_target=qna_project,  ## only needed for specific project within an orchestration projects
            
            # parameters={
            #     qna_project: DeepstackParameters(
            #         language='en'
            #     )
            # }
        )

        with client:
            result = client.conversation_analysis.analyze_conversations(
                params,
                project_name=conv_project,
                deployment_name='production'
            )
        
        assert isinstance(result, ConversationAnalysisResult)

    @GlobalConversationAccountPreparer()
    def test_analysis_with_dictparams(self, conv_account, conv_key, conv_project):
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        params = {
            "query": "One california maki please.",
            "direct_target": conv_project,
            "parameters": {
                conv_project: {
                    "project_type": 'luis_deepstack',
                    "language": "en"
                }
            }
        }

        with client:
            result = client.conversation_analysis.analyze_conversations(
                params,
                project_name=conv_project,
                deployment_name='production'
            )
        
        assert isinstance(result, ConversationAnalysisResult)
 