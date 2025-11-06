# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii_async.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation (async).

USAGE:
    python sample_conversation_pii_async.py

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

# [START conversation_pii_async]
import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    ParticipantRole,
    AnalyzeConversationOperationInput,
    PiiOperationAction,
    ConversationPiiActionContent,
    AnalyzeConversationOperationResult,
    ConversationPiiOperationResult,
    InputWarning,
    ConversationError,
)


async def sample_conversation_pii_async():
    # get settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]

    credential = DefaultAzureCredential()

    entities_detected = []

    async with ConversationAnalysisClient(endpoint, credential=credential) as client:
        # build input
        ml_input = MultiLanguageConversationInput(
            conversations=[
                TextConversation(
                    id="1",
                    language="en",
                    conversation_items=[
                        TextConversationItem(
                            id="1",
                            participant_id="Agent_1",
                            role=ParticipantRole.AGENT,
                            text="Can you provide your name?",
                        ),
                        TextConversationItem(
                            id="2",
                            participant_id="Customer_1",
                            role=ParticipantRole.CUSTOMER,
                            text="Hi, my name is John Doe.",
                        ),
                        TextConversationItem(
                            id="3",
                            participant_id="Agent_1",
                            role=ParticipantRole.AGENT,
                            text="Thank you John, that has been updated in our system.",
                        ),
                    ],
                )
            ]
        )

        pii_action = PiiOperationAction(
            action_content=ConversationPiiActionContent(),
            name="Conversation PII",
        )

        operation_input = AnalyzeConversationOperationInput(
            conversation_input=ml_input,
            actions=[pii_action],
        )

        # start async long-running operation
        poller = await client.begin_analyze_conversation_job(body=operation_input)

        # operation metadata
        print(f"Operation ID: {poller.details.get('operation_id')}")

        # wait for completion
        paged_actions = await poller.result()

        # final-state metadata
        d = poller.details
        print(f"Job ID: {d.get('job_id')}")
        print(f"Status: {d.get('status')}")
        print(f"Created: {d.get('created_date_time')}")
        print(f"Last Updated: {d.get('last_updated_date_time')}")
        if d.get("expiration_date_time"):
            print(f"Expires: {d.get('expiration_date_time')}")
        if d.get("display_name"):
            print(f"Display Name: {d.get('display_name')}")

        # iterate results
        async for actions_page in paged_actions:
            print(
                f"Completed: {actions_page.completed}, "
                f"In Progress: {actions_page.in_progress}, "
                f"Failed: {actions_page.failed}, "
                f"Total: {actions_page.total}"
            )

            for action_result in actions_page.task_results or []:
                print(f"\nAction Name: {action_result.name}")
                print(f"Action Status: {action_result.status}")
                print(f"Kind: {action_result.kind}")

                if isinstance(action_result, ConversationPiiOperationResult):
                    for conversation in action_result.results.conversations or []:
                        print(f"Conversation: #{conversation.id}")
                        print("Detected Entities:")

                        for item in conversation.conversation_items or []:
                            for entity in item.entities or []:
                                print(f"  Category: {entity.category}")
                                print(f"  Subcategory: {entity.subcategory}")
                                print(f"  Text: {entity.text}")
                                print(f"  Offset: {entity.offset}")
                                print(f"  Length: {entity.length}")
                                print(f"  Confidence score: {entity.confidence_score}\n")
                                entities_detected.append(entity)

                        if conversation.warnings:
                            print("Warnings:")
                            for warning in conversation.warnings:
                                if isinstance(warning, InputWarning):
                                    print(f"  Code: {warning.code}")
                                    print(f"  Message: {warning.message}")
                        print()
                else:
                    print("  [No supported results to display for this action type]")

        # errors
        if d.get("errors"):
            print("\nErrors:")
            for err in d["errors"]:
                print(f"  Code: {err.code} - {err.message}")


# [END conversation_pii_async]


async def main():
    await sample_conversation_pii_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
