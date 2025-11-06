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

# [START conversation_pii_with_no_mask_policy]
import os

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
    NoMaskPolicyType,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    NamedEntity,
    ConversationError,
)


def sample_conversation_pii_with_no_mask_policy():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    detected_entities = []

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

    # action with NoMaskPolicyType (detect but do not redact)
    pii_action = PiiOperationAction(
        action_content=ConversationPiiActionContent(redaction_policy=NoMaskPolicyType()),
        name="Conversation PII with No Mask Policy",
    )

    operation_input = AnalyzeConversationOperationInput(
        conversation_input=ml_input,
        actions=[pii_action],
    )

    # start long-running job (sync)
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
                        # NoMaskPolicyType returns original text (no redaction)
                        returned_text = (item.redacted_content.text or "").strip()
                        if not returned_text:
                            continue

                        if item.entities:
                            for entity in item.entities:
                                ent_text = entity.text or ""
                                detected_entities.append(ent_text)
                                if ent_text not in returned_text:
                                    print(f"WARNING: Expected entity '{ent_text}' in returned text but not found.")


# [END conversation_pii_with_no_mask_policy]


def main():
    sample_conversation_pii_with_no_mask_policy()


if __name__ == "__main__":
    main()
