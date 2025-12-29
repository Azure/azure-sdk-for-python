# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_summarization_async.py

DESCRIPTION:
    This sample demonstrates how to summarize a conversation using CLU's conversation
    summarization capability (async).

USAGE:
    python sample_conversation_summarization_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_ENDPOINT
      - AZURE_CONVERSATIONS_KEY
"""

# [START conversation_summarization_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    TextConversationItem,
    TextConversation,
    ParticipantRole,
    MultiLanguageConversationInput,
    SummarizationOperationAction,
    ConversationSummarizationActionContent,
    SummaryAspect,
    AnalyzeConversationOperationInput,
    SummarizationOperationResult,
    ConversationError,
)


async def sample_conversation_summarization_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    # Build conversation input
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

    # Build the operation input and inline actions
    operation_input = AnalyzeConversationOperationInput(
        conversation_input=conversation_input,
        actions=[
            SummarizationOperationAction(
                name="Issue task",
                action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.ISSUE]),
            ),
            SummarizationOperationAction(
                name="Resolution task",
                action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.RESOLUTION]),
            ),
        ],
    )

    async with ConversationAnalysisClient(endpoint, credential=credential) as client:
        poller = await client.begin_analyze_conversation_job(body=operation_input)

        # Operation ID
        op_id = poller.details.get("operation_id")
        if op_id:
            print(f"Operation ID: {op_id}")

        # Wait for result
        paged_actions = await poller.result()

        # Final-state metadata
        d = poller.details
        print(f"Job ID: {d.get('job_id')}")
        print(f"Status: {d.get('status')}")
        print(f"Created: {d.get('created_date_time')}")
        print(f"Last Updated: {d.get('last_updated_date_time')}")
        if d.get("expiration_date_time"):
            print(f"Expires: {d.get('expiration_date_time')}")
        if d.get("display_name"):
            print(f"Display Name: {d.get('display_name')}")

        # Iterate results
        async for actions_page in paged_actions:
            print(
                f"Completed: {actions_page.completed}, "
                f"In Progress: {actions_page.in_progress}, "
                f"Failed: {actions_page.failed}, "
                f"Total: {actions_page.total}"
            )

            for action_result in actions_page.task_results or []:
                if isinstance(action_result, SummarizationOperationResult):
                    for conversation in action_result.results.conversations or []:
                        print(f"  Conversation ID: {conversation.id}")
                        print("  Summaries:")
                        for summary in conversation.summaries or []:
                            print(f"    Aspect: {summary.aspect}")
                            print(f"    Text: {summary.text}")
                        if conversation.warnings:
                            print("  Warnings:")
                            for warning in conversation.warnings:
                                print(f"    Code: {warning.code}, Message: {warning.message}")
                else:
                    print("  [No supported results to display for this action type]")

        # Errors
        if d.get("errors"):
            print("\nErrors:")
            for error in d["errors"]:
                if isinstance(error, ConversationError):
                    print(f"  Code: {error.code} - {error.message}")


# [END conversation_summarization_async]


async def main():
    await sample_conversation_summarization_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
