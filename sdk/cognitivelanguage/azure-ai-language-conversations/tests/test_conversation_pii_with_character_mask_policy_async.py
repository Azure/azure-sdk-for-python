# pylint: disable=line-too-long,useless-suppression
import functools
from typing import cast, List

import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.async_paging import AsyncItemPaged
from azure.ai.language.conversations.aio import ConversationAnalysisClient, AnalyzeConversationAsyncLROPoller
from azure.ai.language.conversations.models import (
    AnalyzeConversationOperationInput,
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    AnalyzeConversationOperationAction,
    PiiOperationAction,
    ConversationPiiActionContent,
    ConversationActions,
    AnalyzeConversationOperationResult,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    NamedEntity,
    ConversationError,
    CharacterMaskPolicyType,
    RedactionCharacter,
)
from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.cognitiveservices.azure.com/",
    conversations_key="fake_key",
)


class TestConversations(AzureRecordedTestCase):

    # Start with any helper functions you might need, for example a client creation method:
    async def create_client(self, endpoint, key):
        credential = AzureKeyCredential(key)
        client = ConversationAnalysisClient(endpoint, credential)
        return client

    ...


class TestConversationsCase(TestConversations):
    @ConversationsPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_conversation_pii_with_character_mask_policy_async(self, conversations_endpoint, conversations_key):
        client = await self.create_client(conversations_endpoint, conversations_key)

        try:
            redacted_verified: List[str] = []

            # ---- Redaction policy: mask with '*' ---------------------------------
            redaction_policy = CharacterMaskPolicyType(redaction_character=RedactionCharacter.ASTERISK)

            # ---- Build input -----------------------------------------------------
            ml_input = MultiLanguageConversationInput(
                conversations=[
                    TextConversation(
                        id="1",
                        language="en",
                        conversation_items=[
                            TextConversationItem(id="1", participant_id="Agent_1", text="Can you provide your name?"),
                            TextConversationItem(id="2", participant_id="Customer_1", text="Hi, my name is John Doe."),
                            TextConversationItem(
                                id="3",
                                participant_id="Agent_1",
                                text="Thank you John, that has been updated in our system.",
                            ),
                        ],
                    )
                ]
            )

            # Action with CharacterMaskPolicyType
            pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
                action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
                name="Conversation PII with Character Mask Policy",
            )
            actions: List[AnalyzeConversationOperationAction] = [pii_action]

            operation_input = AnalyzeConversationOperationInput(
                conversation_input=ml_input,
                actions=actions,
            )

            # ---- Begin LRO ------------------------------------------------------
            poller: AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]] = (
                await client.begin_analyze_conversation_job(body=operation_input)
            )

            # Metadata available immediately
            print(f"Operation ID: {poller.details.get('operation_id')}")

            # Wait for completion; result is AsyncItemPaged[ConversationActions]
            paged_actions: AsyncItemPaged[ConversationActions] = await poller.result()

            # Final-state metadata
            d = poller.details
            print(f"Job ID: {d.get('job_id')}")
            print(f"Status: {d.get('status')}")
            if d.get("errors"):
                print("Errors:")
                for err in d["errors"]:
                    err = cast(ConversationError, err)
                    print(f"  Code: {err.code} - {err.message}")

            # ---- Iterate results and verify redaction ---------------------------
            async for actions_page in paged_actions:
                for action_result in actions_page.task_results or []:
                    ar = cast(AnalyzeConversationOperationResult, action_result)
                    if isinstance(ar, ConversationPiiOperationResult):
                        for conversation in ar.results.conversations or []:
                            conversation = cast(ConversationalPiiResult, conversation)
                            for item in conversation.conversation_items or []:
                                item = cast(ConversationPiiItemResult, item)
                                redacted_text = (getattr(item.redacted_content, "text", None) or "").strip()
                                if not redacted_text:
                                    continue

                                # Only verify when there are detected entities in the original item
                                if item.entities:
                                    for entity in item.entities or []:
                                        ent_text = cast(NamedEntity, entity).text or ""
                                        assert (
                                            ent_text not in redacted_text
                                        ), f"Expected entity '{ent_text}' to be redacted but found in: {redacted_text}"
                                    assert "*" in redacted_text, f"Expected '*' in redacted text, got: {redacted_text}"
                                    redacted_verified.append(redacted_text)

            # ---- Assertions ------------------------------------------------------
            assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}
            assert len(redacted_verified) > 0, "Expected at least one redacted line to be verified."
        finally:
            await client.close()
