# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient, AnalyzeConversationLROPoller
from azure.core.paging import ItemPaged
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
from typing import cast, List
from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.cognitiveservices.azure.com/",
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
    def test_conversation_summarization(self, conversations_endpoint, conversations_key):
        conversation_client = self.create_client(conversations_endpoint, conversations_key)

        # Construct conversation input
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

        # Construct summarization actions
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

        # Wrap into operation input
        operation_input = AnalyzeConversationOperationInput(
            conversation_input=conversation_input, actions=cast(List[AnalyzeConversationOperationAction], actions)
        )

        # ---- begin_* now returns AnalyzeConversationLROPoller[ItemPaged[ConversationActions]]
        poller: AnalyzeConversationLROPoller[ItemPaged[ConversationActions]] = (
            conversation_client.begin_analyze_conversation_job(body=operation_input)
        )

        # You can read operation id immediately (from initial response headers)
        print(f"Operation ID: {poller.details.get('operation_id')}")

        # Result is an ItemPaged[ConversationActions]
        paged_actions: ItemPaged[ConversationActions] = poller.result()

        # Final-state metadata is available after completion via poller.details
        d = poller.details
        print(f"Job ID: {d.get('job_id')}")
        print(f"Status: {d.get('status')}")
        print(f"Created: {d.get('created_date_time')}")
        print(f"Last Updated: {d.get('last_updated_date_time')}")
        if d.get("expiration_date_time"):
            print(f"Expires: {d.get('expiration_date_time')}")
        if d.get("display_name"):
            print(f"Display Name: {d.get('display_name')}")

        # Iterate items; each iteration yields a ConversationActions (your implementation pages by next_link)
        for actions_page in paged_actions:
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

        # Print errors (now exposed via poller.details from the final state)
        if d.get("errors"):
            print("\nErrors:")
            for error in d["errors"]:
                print(f"  Code: {error.code} - {error.message}")
