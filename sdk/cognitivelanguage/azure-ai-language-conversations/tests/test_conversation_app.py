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
    CustomConversationalTaskResult,
    ConversationPrediction
)


class ConversationAppTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_conversation_app(self, endpoint, key, conv_project_name, conv_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = client.analyze_conversation(
                body={
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
            assert result.results.prediction.top_intent == 'Read'
            assert len(result.results.prediction.intents) > 0
            assert result.results.prediction.intents[0].category == 'Read'
            assert result.results.prediction.intents[0].confidence > 0
            # assert - entities
            assert len(result.results.prediction.entities) > 0
            assert result.results.prediction.entities[0].category == 'Contact'
            assert result.results.prediction.entities[0].text == 'Carol'
            assert result.results.prediction.entities[0].confidence > 0
 