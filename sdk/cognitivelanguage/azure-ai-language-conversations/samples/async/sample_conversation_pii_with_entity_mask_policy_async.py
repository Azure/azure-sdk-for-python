# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_conversation_pii_with_entity_mask_policy_async.py

DESCRIPTION:
    This sample demonstrates how to run a PII detection action over a conversation
    using the `EntityMaskPolicyType` in async mode, which redacts detected PII by
    replacing it with an entity category mask such as `[Person]` or `[Person-1]`.

USAGE:
    python sample_conversation_pii_with_entity_mask_policy_async.py

REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_ENDPOINT
    AZURE_CONVERSATIONS_KEY
"""

# [START conversation_pii_with_entity_mask_policy_async]
import os
import re
import asyncio
from typing import List, cast

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.aio import ConversationAnalysisClient
from azure.ai.language.conversations.aio import AnalyzeConversationAsyncLROPoller
from azure.ai.language.conversations.models import (
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    ParticipantRole,
    AnalyzeConversationOperationInput,
    AnalyzeConversationOperationAction,
    PiiOperationAction,
    ConversationPiiActionContent,
    EntityMaskTypePolicyType,
    AnalyzeConversationOperationResult,
    ConversationActions,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    NamedEntity,
    ConversationError,
)
from azure.core.async_paging import AsyncItemPaged


async def sample_conversation_pii_with_entity_mask_policy_async():
    # get secrets
    clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

    client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))

    try:
        redacted_verified: List[str] = []

        # build input
        ml_input = MultiLanguageConversationInput(
            conversations=[
                TextConversation(
                    id="1",
                    language="en",
                    conversation_items=[
                        TextConversationItem(id="1", participant_id="Agent_1", role=ParticipantRole.AGENT, text="Can you provide your name?"),
                        TextConversationItem(id="2", participant_id="Customer_1", role=ParticipantRole.CUSTOMER, text="Hi, my name is John Doe."),
                        TextConversationItem(id="3", participant_id="Agent_1", role=ParticipantRole.AGENT, text="Thank you John, that has been updated in our system."),
                    ],
                )
            ]
        )

        # action with EntityMaskTypePolicyType
        redaction_policy = EntityMaskTypePolicyType()
        pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
            action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
            name="Conversation PII with Entity Mask Policy",
        )
        actions: List[AnalyzeConversationOperationAction] = [pii_action]

        operation_input = AnalyzeConversationOperationInput(
            conversation_input=ml_input,
            actions=actions,
        )

        # start long-running job
        poller: AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]] = (
            await client.begin_analyze_conversation_job(body=operation_input)
        )

        print(f"Operation ID: {poller.details.get('operation_id')}")

        # wait for result
        paged_actions: AsyncItemPaged[ConversationActions] = await poller.result()

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
        async for actions_page in paged_actions:
            for action_result in actions_page.task_results or []:
                ar = cast(AnalyzeConversationOperationResult, action_result)
                if isinstance(ar, ConversationPiiOperationResult):
                    for conversation in ar.results.conversations or []:
                        conversation = cast(ConversationalPiiResult, conversation)
                        for item in conversation.conversation_items or []:
                            item = cast(ConversationPiiItemResult, item)
                            redacted_text = (getattr(item.redacted_content, "text", None) or "").strip()

                            if item.entities and redacted_text:
                                for entity in item.entities:
                                    entity = cast(NamedEntity, entity)
                                    original_text = entity.text or ""

                                    # 1) original PII must be removed
                                    assert (
                                        original_text not in redacted_text
                                    ), f"Expected entity '{original_text}' to be redacted but found in: {redacted_text}"

                                    # 2) mask should appear like [Person] or [Person-1]
                                    expected_mask_pattern = rf"\[{re.escape(entity.category)}-?\d*\]"
                                    assert re.search(expected_mask_pattern, redacted_text, flags=re.IGNORECASE), (
                                        f"Expected entity mask similar to '[{entity.category}]' but got: {redacted_text}"
                                    )

                                redacted_verified.append(redacted_text)

        # assertions
        assert len(redacted_verified) > 0, "Expected at least one redacted line to be verified."
        assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(sample_conversation_pii_with_entity_mask_policy_async())
# [END conversation_pii_with_entity_mask_policy_async]