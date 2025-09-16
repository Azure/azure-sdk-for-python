# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.async_paging import AsyncItemPaged
from azure.ai.language.conversations.aio import ConversationAnalysisClient, AnalyzeConversationAsyncLROPoller
from azure.ai.language.conversations.models import (
    AnalyzeConversationActionResult,
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    StringIndexType,
    ConversationLanguageUnderstandingInput,
    OrchestrationPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationActionResult,
)
from typing import cast, List
from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    conversations_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):
    # Async client factory
    async def create_async_client(self, endpoint: str, key: str) -> ConversationAnalysisClient:
        credential = AzureKeyCredential(key)
        return ConversationAnalysisClient(endpoint, credential)


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_orchestration_prediction_async(self, conversations_endpoint, conversations_key):
        client = await self.create_async_client(conversations_endpoint, conversations_key)
        try:
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
                action_content=ConversationActionContent(
                    project_name=project_name,
                    deployment_name=deployment_name,
                    string_index_type=StringIndexType.UTF16_CODE_UNIT,
                ),
            )

            # Call async API
            response: AnalyzeConversationActionResult = await client.analyze_conversation(data)

            # Cast to the specific discriminator subtype (C#-style)
            conversation_result = cast(ConversationActionResult, response)
            prediction = conversation_result.result.prediction

            assert isinstance(prediction, OrchestrationPrediction)

            # top_intent is Optional[str] in the model; guard to satisfy type checker
            assert prediction.top_intent is not None, "top_intent missing in orchestration prediction"
            responding_project_name = cast(str, prediction.top_intent)
            print(f"Top intent: {responding_project_name}")

            target_intent_result = prediction.intents[responding_project_name]
            assert isinstance(target_intent_result, QuestionAnsweringTargetIntentResult)

            qa = target_intent_result.result
            for ans in qa.answers:  # type: ignore
                print(ans.answer or "")

            # Final assertions like in C#
            assert responding_project_name == "ChitChat-QnA"
        finally:
            await client.close()
