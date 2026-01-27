# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii_with_entity_mask_policy.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation
    using the `EntityMaskPolicyType` in sync mode, which redacts detected PII by
    replacing it with an entity category mask such as `[Person]` or `[Person-1]`.

USAGE:
    python sample_conversation_pii_with_entity_mask_policy.py

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

# [START conversation_pii_with_entity_mask_policy]
import os
import re

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    ParticipantRole,
    AnalyzeConversationOperationInput,
    PiiOperationAction,
    ConversationPiiActionContent,
    EntityMaskTypePolicyType,
    ConversationPiiOperationResult,
)


def sample_conv_pii_entity_mask_policy():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    redacted_verified = []

    client = ConversationAnalysisClient(endpoint, credential=credential)

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

    # action with EntityMaskTypePolicyType
    redaction_policy = EntityMaskTypePolicyType()
    pii_action = PiiOperationAction(
        action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
        name="Conversation PII with Entity Mask Policy",
    )

    operation_input = AnalyzeConversationOperationInput(
        conversation_input=ml_input,
        actions=[pii_action],
    )

    # start long-running job
    poller = client.begin_analyze_conversation_job(body=operation_input)
    print(f"Operation ID: {poller.details.get('operation_id')}")

    # wait for result
    paged_actions = poller.result()

    # final metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    if d.get("errors"):
        print("Errors:")
        for err in d["errors"]:
            print(f"  Code: {err.code} - {err.message}")

    # iterate results
    for actions_page in paged_actions:
        for action_result in actions_page.task_results or []:
            if isinstance(action_result, ConversationPiiOperationResult):
                for conversation in action_result.results.conversations or []:
                    for item in conversation.conversation_items or []:
                        redacted_text = (item.redacted_content.text or "").strip()
                        if not redacted_text:
                            continue
                        if item.entities and redacted_text:
                            all_ok = True
                            for entity in item.entities:
                                original_text = entity.text or ""
                                # 1) original PII must be removed
                                if original_text and original_text in redacted_text:
                                    print(
                                        f"WARNING: Expected entity '{original_text}' to be redacted "
                                        f"but found in: {redacted_text}"
                                    )
                                    all_ok = False
                                # 2) mask should appear like [Person] or [Person-1]
                                expected_mask_pattern = rf"\[{re.escape(entity.category)}-?\d*\]"
                                if not re.search(expected_mask_pattern, redacted_text, flags=re.IGNORECASE):
                                    print(
                                        f"WARNING: Expected entity mask similar to "
                                        f"'[{entity.category}]' but got: {redacted_text}"
                                    )
                                    all_ok = False
                            if all_ok:
                                redacted_verified.append(redacted_text)


# [END conversation_pii_with_entity_mask_policy]


def main():
    sample_conv_pii_entity_mask_policy()


if __name__ == "__main__":
    main()
