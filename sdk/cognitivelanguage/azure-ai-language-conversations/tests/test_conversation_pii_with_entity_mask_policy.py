# pylint: disable=line-too-long,useless-suppression
import functools
import pytest

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.language.conversations import ConversationAnalysisClient, AnalyzeConversationLROPoller
from azure.core.paging import ItemPaged
from azure.ai.language.conversations.models import (
    # request models
    AnalyzeConversationOperationInput,
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    PiiOperationAction,
    ConversationPiiActionContent,
    ConversationActions,
    AnalyzeConversationOperationResult,
    ConversationPiiOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    NamedEntity,
    InputWarning,
    ConversationError,
    AnalyzeConversationOperationAction,
    CharacterMaskPolicyType,
    RedactionCharacter,
    EntityMaskTypePolicyType,
)
from typing import cast, List
import re

from azure.core.credentials import AzureKeyCredential

ConversationsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "conversations",
    conversations_endpoint="https://Sanitized.azure-api.net/",
    conversations_key="fake_key",
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
    def test_conversation_pii_with_entity_mask_policy(self, conversations_endpoint, conversations_key):
        client = self.create_client(conversations_endpoint, conversations_key)

        # Track redacted texts we verify
        redacted_verified: List[str] = []

        # ---- Redaction policy: mask entities as [Category] / [Category-1] ----
        redaction_policy = EntityMaskTypePolicyType()

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

        # Action with EntityMaskTypePolicyType
        pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
            action_content=ConversationPiiActionContent(redaction_policy=redaction_policy),
            name="Conversation PII with Entity Mask Policy",
        )
        actions: List[AnalyzeConversationOperationAction] = [pii_action]

        operation_input = AnalyzeConversationOperationInput(
            conversation_input=ml_input,
            actions=actions,
        )

        # ---- Begin LRO -------------------------------------------------------
        poller: AnalyzeConversationLROPoller[ItemPaged[ConversationActions]] = client.begin_analyze_conversation_job(
            body=operation_input
        )

        print(f"Operation ID: {poller.details.get('operation_id')}")

        # Result: ItemPaged[ConversationActions]
        paged_actions: ItemPaged[ConversationActions] = poller.result()

        # Final-state metadata
        d = poller.details
        print(f"Job ID: {d.get('job_id')}")
        print(f"Status: {d.get('status')}")
        if d.get("errors"):
            print("Errors:")
            for err in d["errors"]:
                err = cast(ConversationError, err)
                print(f"  Code: {err.code} - {err.message}")

        # ---- Iterate results and validate redaction --------------------------
        for actions_page in paged_actions:
            for action_result in actions_page.task_results or []:
                ar = cast(AnalyzeConversationOperationResult, action_result)
                print(f"\nAction Name: {getattr(ar, 'name', None)}")

                if isinstance(ar, ConversationPiiOperationResult):
                    for conversation in ar.results.conversations or []:
                        conversation = cast(ConversationalPiiResult, conversation)
                        print(f"Conversation: #{conversation.id}")

                        for item in conversation.conversation_items or []:
                            item = cast(ConversationPiiItemResult, item)
                            redacted_text = (getattr(item.redacted_content, "text", None) or "").strip()
                            print(f"Redacted Text: {redacted_text}")

                            # Only verify when there are detected entities in the original item
                            if item.entities and redacted_text:
                                for entity in item.entities:
                                    entity = cast(NamedEntity, entity)
                                    original_text = entity.text or ""
                                    # 1) original PII should not be present
                                    assert (
                                        original_text not in redacted_text
                                    ), f"Expected entity '{original_text}' to be redacted but found in: {redacted_text}"

                                    # 2) redaction should show an entity mask like [Person] or [Person-1]
                                    expected_mask_pattern = rf"\[{re.escape(entity.category)}-?\d*\]"
                                    assert re.search(expected_mask_pattern, redacted_text, flags=re.IGNORECASE), (
                                        f"Expected redacted text to contain an entity mask similar to "
                                        f"'[{entity.category}]' but got: {redacted_text}"
                                    )

                                redacted_verified.append(redacted_text)

        # ---- Assertions -------------------------------------------------------
        assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}
        assert len(redacted_verified) > 0, "Expected at least one redacted line to be verified."
