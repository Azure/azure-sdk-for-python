# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient
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
)
from typing import cast, List
from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    PowerShellPreparer,
    "authoring",
    authoring_endpoint="fake_resource.servicebus.windows.net/",
    authoring_key="fake_key",
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
    def test_create_project(self, authoring_endpoint, authoring_key):
        conversation_client = self.create_client(authoring_endpoint, authoring_key)

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

        # Call the API
        response = conversation_client.begin_analyze_conversation_job(body=operation_input).result()

        # Validate response and print results
        print(f"Job ID: {response.job_id}")
        print(f"Status: {response.status}")
        print(f"Created: {response.created_date_time}")
        print(f"Last Updated: {response.last_updated_date_time}")
        if response.expiration_date_time:
            print(f"Expires: {response.expiration_date_time}")
        if response.display_name:
            print(f"Display Name: {response.display_name}")

        for action_result in response.actions.items_property or []:
            print(f"\nAction Name: {action_result.name}")
            print(f"Action Status: {action_result.status}")
            print(f"Kind: {action_result.kind}")

            # Safely check if this is a summarization result
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

        # Print errors, if any
        if response.errors:
            print("\nErrors:")
            for error in response.errors:
                print(f"  Code: {error.code} - {error.message}")
