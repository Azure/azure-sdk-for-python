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
    LUISTargetIntentResult,
    OrchestratorPrediction,
    CustomConversationalTask,
    ConversationAnalysisOptions,
    CustomConversationTaskParameters,
    TextConversationItem
)

class OrchestrationAppLuisResponseAsyncTests(AsyncConversationTest):

    @GlobalConversationAccountPreparer()
    async def test_orchestration_app_luis_response(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        async with client:
            query = "Reserve a table for 2 at the Italian restaurant"
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
            top_project = "RestaurantIntent"
            assert not result is None
            assert isinstance(result, CustomConversationalTaskResult)
            assert result.results.query == query
            # assert - prediction type
            assert isinstance(result.results.prediction, OrchestratorPrediction)
            assert result.results.prediction.project_kind == "workflow"
            # assert - top matching project
            assert result.results.prediction.top_intent == top_project
            top_intent_object = result.results.prediction.intents[top_project]
            assert isinstance(top_intent_object, LUISTargetIntentResult)
            assert top_intent_object.target_kind == "luis"
            # assert intent and entities
            top_intent = "Reserve"
            luis_result = top_intent_object.result["prediction"]
            assert luis_result["topIntent"] == top_intent
            assert len(luis_result["intents"]) > 0
            assert luis_result["intents"][top_intent]["score"] > 0
            # assert - entities
            assert len(luis_result["entities"]) > 0

