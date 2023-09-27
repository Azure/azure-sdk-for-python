# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.ai.language.conversations import ConversationAnalysisClient
from azure.core.credentials import AzureKeyCredential
from devtools_testutils import AzureRecordedTestCase


class TestConversationApp(AzureRecordedTestCase):

    def test_conversation_app(self, recorded_test, conversation_creds):

        # analyze query
        client = ConversationAnalysisClient(
            conversation_creds["endpoint"],
            AzureKeyCredential(conversation_creds["key"])
        )
        with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = client.analyze_conversation(
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
                        "projectName": conversation_creds["conv_project_name"],
                        "deploymentName": conversation_creds["conv_deployment_name"],
                        "verbose": True
                    }
                }
            )

            # assert - main object
            assert not result is None
            assert result["kind"] == "ConversationResult"

            # assert - prediction type
            assert result["result"]["query"] == query
            assert result["result"]["prediction"]["projectKind"] == 'Conversation'

            # assert - top intent
            assert result["result"]["prediction"]["topIntent"] == 'Send'
            assert len(result["result"]["prediction"]["intents"]) > 0
            assert result["result"]["prediction"]["intents"][0]["category"] == 'Send'
            assert result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0

            # assert - entities
            assert len(result["result"]["prediction"]["entities"]) > 0
            assert result["result"]["prediction"]["entities"][0]["category"] == 'Contact'
            assert result["result"]["prediction"]["entities"][0]["text"] == 'Carol'
            assert result["result"]["prediction"]["entities"][0]["confidenceScore"] > 0

    @pytest.mark.skip("no runtime AAD yet for 2023-04-01")
    def test_conversation_app_aad_auth(self, recorded_test, conversation_creds):
        token = self.get_credential(ConversationAnalysisClient)
        client = ConversationAnalysisClient(conversation_creds["endpoint"], token)
        with client:
            query = "Send an email to Carol about the tomorrow's demo"
            result = client.analyze_conversation(
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
                        "projectName": conversation_creds["conv_project_name"],
                        "deploymentName": conversation_creds["conv_deployment_name"],
                        "verbose": True
                    }
                }
            )

            # assert - main object
            assert not result is None
            assert result["kind"] == "ConversationResult"

            # assert - prediction type
            assert result["result"]["query"] == query
            assert result["result"]["prediction"]["projectKind"] == 'Conversation'

            # assert - top intent
            assert result["result"]["prediction"]["topIntent"] == 'Send'
            assert len(result["result"]["prediction"]["intents"]) > 0
            assert result["result"]["prediction"]["intents"][0]["category"] == 'Send'
            assert result["result"]["prediction"]["intents"][0]["confidenceScore"] > 0

            # assert - entities
            assert len(result["result"]["prediction"]["entities"]) > 0
            assert result["result"]["prediction"]["entities"][0]["category"] == 'Contact'
            assert result["result"]["prediction"]["entities"][0]["text"] == 'Carol'
            assert result["result"]["prediction"]["entities"][0]["confidenceScore"] > 0
