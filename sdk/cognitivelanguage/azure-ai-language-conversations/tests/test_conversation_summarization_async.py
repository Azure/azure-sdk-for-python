# pylint: disable=line-too-long,useless-suppression
import functools
from typing import cast, List

import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.async_paging import AsyncItemPaged
from azure.ai.language.conversations.aio import ConversationAnalysisClient, AnalyzeConversationAsyncLROPoller
from azure.ai.language.conversations.models import (
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    SummarizationOperationAction,
    ConversationSummarizationActionContent,
    SummaryAspect,
    AnalyzeConversationOperationInput,
    ParticipantRole,
    AnalyzeConversationOperationAction,
    SummarizationOperationResult,
    ConversationActions,
)
from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    conversations_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    async def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_conversation_summarization_async(self, conversations_endpoint, conversations_key):
        client = await self.create_client(conversations_endpoint, conversations_key)

        try:
            # Build conversation input (same as sync)
            conversation_items = [
                TextConversationItem(
                    id="1", participant_id="Agent_1", text="Hello, how can I help you?", role=ParticipantRole.AGENT
                ),
                TextConversationItem(
                    id="2",
                    participant_id="Customer_1",
                    text="How to upgrade Office? I am getting error messages the whole day.",
                    role=ParticipantRole.CUSTOMER,
                ),
                TextConversationItem(
                    id="3",
                    participant_id="Agent_1",
                    text="Press the upgrade button please. Then sign in and follow the instructions.",
                    role=ParticipantRole.AGENT,
                ),
            ]
            conversation_input = MultiLanguageConversationInput(
                conversations=[TextConversation(id="1", language="en", conversation_items=conversation_items)]
            )

            actions = [
                SummarizationOperationAction(
                    name="Issue task",
                    action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.ISSUE]),
                ),
                SummarizationOperationAction(
                    name="Resolution task",
                    action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.RESOLUTION]),
                ),
            ]

            operation_input = AnalyzeConversationOperationInput(
                conversation_input=conversation_input,
                actions=cast(List[AnalyzeConversationOperationAction], actions),
            )

            # ---- begin_* now returns AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]]
            async with client:
                poller: AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]] = (
                    await client.begin_analyze_conversation_job(body=operation_input, content_type="application/json")
                )

                # Operation id is available immediately
                op_id = poller.details.get("operation_id")
                if op_id:
                    print(f"Operation ID: {op_id}")

                # Result is AsyncItemPaged[ConversationActions]
                paged_actions: AsyncItemPaged[ConversationActions] = await poller.result()

                # Final-state metadata via poller.details
                d = poller.details
                print(f"Job ID: {d.get('job_id')}")
                print(f"Status: {d.get('status')}")
                print(f"Created: {d.get('created_date_time')}")
                print(f"Last Updated: {d.get('last_updated_date_time')}")
                if d.get("expiration_date_time"):
                    print(f"Expires: {d.get('expiration_date_time')}")
                if d.get("display_name"):
                    print(f"Display Name: {d.get('display_name')}")

                # Iterate items (each item is a ConversationActions)
                async for actions_page in paged_actions:
                    print(
                        f"Completed: {actions_page.completed}, "
                        f"In Progress: {actions_page.in_progress}, "
                        f"Failed: {actions_page.failed}, "
                        f"Total: {actions_page.total}"
                    )

                    for action_result in actions_page.task_results or []:
                        print(f"\nAction Name: {getattr(action_result, 'name', None)}")
                        print(f"Action Status: {getattr(action_result, 'status', None)}")
                        print(f"Kind: {getattr(action_result, 'kind', None)}")

                        if isinstance(action_result, SummarizationOperationResult):
                            for conversation in action_result.results.conversations:
                                print(f"  Conversation ID: {conversation.id}")
                                print("  Summaries:")
                                for summary in conversation.summaries:
                                    print(f"    Aspect: {summary.aspect}")
                                    print(f"    Text: {summary.text}")
                                if conversation.warnings:
                                    print("  Warnings:")
                                    for warning in conversation.warnings:
                                        print(f"    Code: {warning.code}, Message: {warning.message}")
                        else:
                            print("  [No supported results to display for this action type]")

                # Print errors (exposed via poller.details from final state)
                if d.get("errors"):
                    print("\nErrors:")
                    for error in d["errors"]:
                        print(f"  Code: {error.code} - {error.message}")

                # Simple sanity checks
                assert d.get("status") in {"succeeded", "partiallyCompleted", "running", "notStarted"}
        finally:
            await client.close()
