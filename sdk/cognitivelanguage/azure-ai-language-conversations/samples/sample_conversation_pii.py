# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation.

USAGE:
    python sample_conversation_pii.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
"""

# [START conversation_pii]
import os
from typing import List, cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient, AnalyzeConversationLROPoller
from azure.ai.language.conversations.models import (
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    ParticipantRole,
    AnalyzeConversationOperationInput,
    AnalyzeConversationOperationAction,
    PiiOperationAction,
    ConversationPiiActionContent,
    AnalyzeConversationOperationResult,
    ConversationActions,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    NamedEntity,
    InputWarning,
    ConversationError,
)
from azure.core.paging import ItemPaged


def sample_conversation_pii():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

    entities_detected: List[NamedEntity] = []

    # build input
    ml_input = MultiLanguageConversationInput(
        conversations=[
            TextConversation(
                id="1",
                language="en",
                conversation_items=[
                    TextConversationItem(
                        id="1", participant_id="Agent_1", role=ParticipantRole.AGENT, text="Can you provide your name?"
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

    pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
        action_content=ConversationPiiActionContent(),
        name="Conversation PII",
    )
    actions: List[AnalyzeConversationOperationAction] = [pii_action]

    operation_input = AnalyzeConversationOperationInput(
        conversation_input=ml_input,
        actions=actions,
    )

    # start long-running PII analysis job
    poller: AnalyzeConversationLROPoller[ItemPaged[ConversationActions]] = client.begin_analyze_conversation_job(
        body=operation_input
    )

    # operation metadata available immediately
    print(f"Operation ID: {poller.details.get('operation_id')}")

    # wait for completion
    paged_actions: ItemPaged[ConversationActions] = poller.result()

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
    for actions_page in paged_actions:
        print(
            f"Completed: {actions_page.completed}, "
            f"In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, "
            f"Total: {actions_page.total}"
        )

        for action_result in actions_page.task_results or []:
            ar = cast(AnalyzeConversationOperationResult, action_result)
            print(f"\nAction Name: {getattr(ar, 'name', None)}")
            print(f"Action Status: {getattr(ar, 'status', None)}")
            print(f"Kind: {getattr(ar, 'kind', None)}")

            if isinstance(ar, ConversationPiiOperationResult):
                for conversation in ar.results.conversations or []:
                    conversation = cast(ConversationalPiiResult, conversation)
                    print(f"Conversation: #{conversation.id}")
                    print("Detected Entities:")

                    for item in conversation.conversation_items or []:
                        item = cast(ConversationPiiItemResult, item)
                        for entity in item.entities or []:
                            entity = cast(NamedEntity, entity)
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
                            warning = cast(InputWarning, warning)
                            print(f"  Code: {warning.code}")
                            print(f"  Message: {warning.message}")
                    print()
            else:
                print("  [No supported results to display for this action type]")

    # print errors
    if d.get("errors"):
        print("\nErrors:")
        for err in d["errors"]:
            err = cast(ConversationError, err)
            print(f"  Code: {err.code} - {err.message}")

    # assertions
    assert len(entities_detected) > 0, "Expected at least one PII entity."
    assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}


if __name__ == "__main__":
    sample_conversation_pii()
# [END conversation_pii]
