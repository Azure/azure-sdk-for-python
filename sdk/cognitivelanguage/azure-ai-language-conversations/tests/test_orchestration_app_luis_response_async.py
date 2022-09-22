# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase


class TestOrchestrationAppLuisResponseAsync(AzureRecordedTestCase):

    @pytest.mark.skip("https://github.com/Azure/azure-sdk-for-python/issues/24962")
    @pytest.mark.asyncio
    async def test_orchestration_app_luis_response(self, recorded_test, conversation_creds):

        # analyze query
        client = ConversationAnalysisClient(
            conversation_creds["endpoint"],
            AzureKeyCredential(conversation_creds["key"])
        )
        async with client:
            query = "Reserve a table for 2 at the Italian restaurant"
            result = await client.analyze_conversation(
                task={
                    "kind": "Conversation",
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
                        "projectName": conversation_creds["orch_project_name"],
                        "deploymentName": conversation_creds["orch_deployment_name"],
                        "verbose": True
                    }
                }
            )

            # assert - main object
            top_project = "RestaurantIntent"
            assert not result is None
            assert result["kind"] == "ConversationResult"
            assert result["result"]["query"] == query

            # assert - prediction type
            assert result["result"]["prediction"]["projectKind"] == "Orchestration"

            # assert - top matching project
            assert result["result"]["prediction"]["topIntent"] == top_project
            top_intent_object = result["result"]["prediction"]["intents"][top_project]
            assert top_intent_object["targetProjectKind"] == "Luis"

            # assert intent and entities
            top_intent = "Reserve"
            luis_result = top_intent_object["result"]["prediction"]
            assert luis_result["topIntent"] == top_intent
            assert len(luis_result["intents"]) > 0
            assert luis_result["intents"][top_intent]["score"] > 0

            # assert - entities
            assert len(luis_result["entities"]) > 0
