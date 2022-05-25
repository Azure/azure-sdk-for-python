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
    QuestionAnsweringTargetIntentResult,
    OrchestratorPrediction,
    CustomConversationalTask,
    ConversationAnalysisOptions,
    CustomConversationTaskParameters,
    TextConversationItem
)

class OrchestrationAppQnaResponseTests(ConversationTest):

    @GlobalConversationAccountPreparer()
    def test_orchestration_app_qna_response(self, endpoint, key, orch_project_name, orch_deployment_name):

        # analyze query
        client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
        with client:
            query = "How are you?"
            result = client.analyze_conversation(
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
            top_project = 'ChitChat-QnA'
            assert not result is None
            assert isinstance(result, CustomConversationalTaskResult)
            assert result.results.query == query
            # assert - prediction type
            assert isinstance(result.results.prediction, OrchestratorPrediction)
            assert result.results.prediction.project_kind == "workflow"
            # assert - top matching project
            assert result.results.prediction.top_intent == top_project
            top_intent_object = result.results.prediction.intents[top_project]
            assert isinstance(top_intent_object, QuestionAnsweringTargetIntentResult)
            assert top_intent_object.target_kind == "question_answering"
            # assert intent and entities
            qna_result = top_intent_object.result
            answer = qna_result.answers[0].answer
            assert not answer is None

