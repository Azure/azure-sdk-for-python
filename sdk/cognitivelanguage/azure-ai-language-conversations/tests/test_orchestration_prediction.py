import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    AnalyzeConversationActionResult,
    ConversationLanguageUnderstandingActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    StringIndexType,
    ConversationLanguageUnderstandingInput,
    OrchestrationPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationActionResult,
)
from typing import cast

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "conversations",
    conversations_endpoint="fake_resource.servicebus.windows.net/",
    conversations_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy
    def test_orchestration_prediction(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        project_name = "TestWorkflow"
        deployment_name = "production"

        # Build request using strongly-typed models
        data = ConversationLanguageUnderstandingInput(
            conversation_input=ConversationAnalysisInput(
                conversation_item=TextConversationItem(
                    id="1",
                    participant_id="participant1",
                    text="How are you?",
                )
            ),
            action_content=ConversationLanguageUnderstandingActionContent(
                project_name=project_name,
                deployment_name=deployment_name,
                string_index_type=StringIndexType.UTF16_CODE_UNIT,
            ),
        )

        response: AnalyzeConversationActionResult = client.analyze_conversation(data)

        conversation_result = cast(ConversationActionResult, response)
        prediction = conversation_result.result.prediction

        assert isinstance(prediction, OrchestrationPrediction)

        assert prediction.top_intent is not None, "top_intent missing in orchestration prediction"
        responding_project_name = cast(str, prediction.top_intent)
        print(f"Top intent: {responding_project_name}")

        target_intent_result = prediction.intents[responding_project_name]
        assert isinstance(target_intent_result, QuestionAnsweringTargetIntentResult)

        qa = target_intent_result.result
        for ans in qa.answers: # type: ignore
            print(ans.answer or "")

        # Final assertions like in C#
        assert responding_project_name == "ChitChat-QnA"
