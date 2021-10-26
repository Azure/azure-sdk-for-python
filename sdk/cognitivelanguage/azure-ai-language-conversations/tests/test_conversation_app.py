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
)


class ConversationAppTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_conversation_app(self, conv_account, conv_key, conv_project):

        # prepare data
        query = "One california maki please."
        input = AnalysisParameters(
            query=query,
        )

        # analyze quey
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                input,
                project_name=conv_project,
                deployment_name='production'
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        # assert isinstance(result.prediction, DeepstackPrediction)
        assert result.prediction.project_kind == 'conversation'
        assert result.prediction.top_intent == 'Order'
        assert len(result.prediction.entities) > 0
        assert len(result.prediction.intents) > 0
        assert result.prediction.intents[0].category == 'Order'
        assert result.prediction.intents[0].confidence_score > 0
        assert result.prediction.entities[0].category == 'OrderItem'
        assert result.prediction.entities[0].text == 'california maki'
        assert result.prediction.entities[0].confidence_score > 0
        

    @GlobalConversationAccountPreparer()
    def test_conversation_app_with_dictparams(self, conv_account, conv_key, conv_project):
        
        # prepare data
        query = "One california maki please."
        params = {
            "query": query,
        }

        # analyze quey
        client = ConversationAnalysisClient(conv_account, AzureKeyCredential(conv_key))
        with client:
            result = client.analyze_conversations(
                params,
                project_name=conv_project,
                deployment_name='production'
            )
        
        # assert
        assert isinstance(result, AnalyzeConversationResult)
        assert result.query == query
        # assert isinstance(result.prediction, DeepstackPrediction)
        assert result.prediction.project_kind == 'conversation'
        assert result.prediction.top_intent == 'Order'
        assert len(result.prediction.entities) > 0
        assert len(result.prediction.intents) > 0
        assert result.prediction.intents[0].category == 'Order'
        assert result.prediction.intents[0].confidence_score > 0
        assert result.prediction.entities[0].category == 'OrderItem'
        assert result.prediction.entities[0].text == 'california maki'
        assert result.prediction.entities[0].confidence_score > 0
 