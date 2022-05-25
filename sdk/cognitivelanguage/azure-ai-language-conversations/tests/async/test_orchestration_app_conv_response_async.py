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
    ConversationTargetIntentResult,
    OrchestratorPrediction,
    CustomConversationalTask,
    ConversationAnalysisOptions,
    CustomConversationTaskParameters,
    TextConversationItem
)

class OrchestrationAppConvResponseAsyncTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_orchestration_app_conv_response(self, endpoint, key, orch_project_name, orch_deployment_name):

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
                        project_name=orch_project_name,
                        deployment_name=orch_deployment_name
                    )
                )
            )
        
            # assert - main object
            top_project = "EmailIntent"
            assert not result is None
            assert isinstance(result, CustomConversationalTaskResult)
            assert result.results.query == query
            # assert - prediction type
            assert isinstance(result.results.prediction, OrchestratorPrediction)
            assert result.results.prediction.project_kind == "workflow"
            # assert - top matching project
            assert result.results.prediction.top_intent == top_project
            top_intent_object = result.results.prediction.intents[top_project]
            assert isinstance(top_intent_object, ConversationTargetIntentResult)
            assert top_intent_object.target_kind == "conversation"
            # assert intent and entities
            conversation_result = top_intent_object.result.prediction
            assert conversation_result.top_intent == 'Setup'
            assert len(conversation_result.intents) > 0
            assert conversation_result.intents[0].category == 'Setup'
            assert conversation_result.intents[0].confidence > 0
            # assert - entities
            assert len(conversation_result.entities) > 0
            assert conversation_result.entities[0].category == 'Contact'
            assert conversation_result.entities[0].text == 'Carol'
            assert conversation_result.entities[0].confidence > 0

