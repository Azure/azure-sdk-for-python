# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii_with_no_mask_policy.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation
    using the `NoMaskPolicyType`, which detects PII but does NOT redact it
    (the original text is returned).

USAGE:
    python sample_conversation_pii_with_no_mask_policy.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
"""

# [START conversation_pii_with_no_mask_policy]
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
    NoMaskPolicyType,
    AnalyzeConversationOperationResult,
    ConversationActions,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    NamedEntity,
    ConversationError,
)
from azure.core.paging import ItemPaged


def sample_conversation_pii_with_no_mask_policy():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

    detected_entities: List[str] = []

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

    # action with NoMaskPolicyType
    redaction_policy = NoMaskPolicyType()
    pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
        action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
        name="Conversation PII with No Mask Policy",
    )
    actions: List[AnalyzeConversationOperationAction] = [pii_action]

    operation_input = AnalyzeConversationOperationInput(
        conversation_input=ml_input,
        actions=actions,
    )

    # start long-running job
    poller: AnalyzeConversationLROPoller[ItemPaged[ConversationActions]] = client.begin_analyze_conversation_job(
        body=operation_input
    )

    print(f"Operation ID: {poller.details.get('operation_id')}")

    # wait for result
    paged_actions: ItemPaged[ConversationActions] = poller.result()

    # final metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    if d.get("errors"):
        print("Errors:")
        for err in d["errors"]:
            err = cast(ConversationError, err)
            print(f"  Code: {err.code} - {err.message}")

    # iterate results
    for actions_page in paged_actions:
        for action_result in actions_page.task_results or []:
            ar = cast(AnalyzeConversationOperationResult, action_result)
            if isinstance(ar, ConversationPiiOperationResult):
                for conversation in ar.results.conversations or []:
                    conversation = cast(ConversationalPiiResult, conversation)
                    for item in conversation.conversation_items or []:
                        item = cast(ConversationPiiItemResult, item)
                        returned_text = (getattr(item.redacted_content, "text", None) or "").strip()
                        if item.entities and returned_text:
                            for entity in item.entities:
                                entity = cast(NamedEntity, entity)
                                ent_text = entity.text or ""
                                detected_entities.append(ent_text)
                                # verify that original PII text is still present
                                assert ent_text in returned_text, f"Expected entity '{ent_text}' in: {returned_text}"

    # assertions
    assert len(detected_entities) > 0, "Expected at least one detected PII entity."
    assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}


if __name__ == "__main__":
    sample_conversation_pii_with_no_mask_policy()
# [END conversation_pii_with_no_mask_policy]
