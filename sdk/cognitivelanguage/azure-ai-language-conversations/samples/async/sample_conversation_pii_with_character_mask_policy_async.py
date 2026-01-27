# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii_with_character_mask_policy_async.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation
    using the `CharacterMaskPolicyType` asynchronously. Detected PII is redacted
    by replacing characters with a mask (e.g., '*').

USAGE:
    python sample_conversation_pii_with_character_mask_policy_async.py

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

# [START conversation_pii_with_character_mask_policy_async]
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
    CharacterMaskPolicyType,
    RedactionCharacter,
    ConversationPiiOperationResult,
)


async def sample_conversation_pii_with_character_mask_policy_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]

    # AAD credential
    credential = DefaultAzureCredential()

    redacted_verified: list[str] = []

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

        # action with CharacterMaskPolicyType
        redaction_policy = CharacterMaskPolicyType(redaction_character=RedactionCharacter.ASTERISK)
        pii_action = PiiOperationAction(
            action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
            name="Conversation PII with Character Mask Policy",
        )

        operation_input = AnalyzeConversationOperationInput(
            conversation_input=ml_input,
            actions=[pii_action],
        )

        # start long-running job
        poller = await client.begin_analyze_conversation_job(body=operation_input)
        print(f"Operation ID: {poller.details.get('operation_id')}")

        # wait for completion
        paged_actions = await poller.result()

        # final metadata
        d = poller.details
        print(f"Job ID: {d.get('job_id')}")
        print(f"Status: {d.get('status')}")
        if d.get("errors"):
            print("Errors:")
            for err in d["errors"]:
                print(f"  Code: {err.code} - {err.message}")

        # iterate results and verify redaction
        async for actions_page in paged_actions:
            for action_result in actions_page.task_results or []:
                if isinstance(action_result, ConversationPiiOperationResult):
                    for conversation in action_result.results.conversations or []:
                        for item in conversation.conversation_items or []:
                            redacted_text = (item.redacted_content.text or "").strip()
                            if not redacted_text:
                                continue

                            if item.entities:
                                for entity in item.entities:
                                    ent_text = entity.text or ""
                                    if ent_text in redacted_text:
                                        print(
                                            f"WARNING: Expected '{ent_text}' to be redacted but found in: {redacted_text}"
                                        )

                                if "*" in redacted_text:
                                    redacted_verified.append(redacted_text)


# [END conversation_pii_with_character_mask_policy_async]


async def main():
    await sample_conversation_pii_with_character_mask_policy_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
