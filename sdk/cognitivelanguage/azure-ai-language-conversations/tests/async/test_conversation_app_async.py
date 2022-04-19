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
    CustomConversationalTaskResult,
    ConversationPrediction,
    CustomConversationalTask,
    ConversationAnalysisOptions,
    CustomConversationTaskParameters,
    TextConversationItem
)


class ConversationAppAsyncTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_conversation_app(self, endpoint, key, conv_project_name, conv_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        async with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = await client.analyze_conversation(
                task=CustomConversationalTask(
                    analysis_input=ConversationAnalysisOptions(
                        conversation_item=TextConversationItem(
                            id=1,
                            participant_id=1,
                            text=query
                        )
                    ),
                    parameters=CustomConversationTaskParameters(
                        project_name=conv_project_name,
                        deployment_name=conv_deployment_name
                    )
                )
            )
        
            # assert - main object
            assert not result is None
            assert isinstance(result, CustomConversationalTaskResult)
            # assert - prediction type
            assert result.results.query == query
            assert isinstance(result.results.prediction, ConversationPrediction)
            assert result.results.prediction.project_kind == 'conversation'
            # assert - top intent
            assert result.results.prediction.top_intent == 'Setup'
            assert len(result.results.prediction.intents) > 0
            assert result.results.prediction.intents[0].category == 'Setup'
            assert result.results.prediction.intents[0].confidence > 0
            # assert - entities
            assert len(result.results.prediction.entities) > 0
            assert result.results.prediction.entities[0].category == 'Contact'
            assert result.results.prediction.entities[0].text == 'Carol'
            assert result.results.prediction.entities[0].confidence > 0
 

    @GlobalConversationAccountPreparer()
    async def test_conversation_app_with_dict_parms(self, endpoint, key, conv_project_name, conv_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        async with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = await client.analyze_conversation(
                task={
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
                        "projectName": conv_project_name,
                        "deploymentName": conv_deployment_name,
                        "verbose": True
                    }
                }
            )
        
            # assert - main object
            assert not result is None
            assert isinstance(result, CustomConversationalTaskResult)
            # assert - prediction type
            assert result.results.query == query
            assert isinstance(result.results.prediction, ConversationPrediction)
            assert result.results.prediction.project_kind == 'conversation'
            # assert - top intent
            assert result.results.prediction.top_intent == 'Setup'
            assert len(result.results.prediction.intents) > 0
            assert result.results.prediction.intents[0].category == 'Setup'
            assert result.results.prediction.intents[0].confidence > 0
            # assert - entities
            assert len(result.results.prediction.entities) > 0
            assert result.results.prediction.entities[0].category == 'Contact'
            assert result.results.prediction.entities[0].text == 'Carol'
            assert result.results.prediction.entities[0].confidence > 0
 