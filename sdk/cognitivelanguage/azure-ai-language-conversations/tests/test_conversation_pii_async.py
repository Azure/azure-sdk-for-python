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
    ConversationPiiOperationResult,
    MultiLanguageConversationInput,
    TextConversation,
    TextConversationItem,
    AnalyzeConversationOperationAction,
    PiiOperationAction,
    ConversationPiiActionContent,
    ConversationActions,
    NamedEntity,
    ConversationError,
    AnalyzeConversationOperationResult,
    ConversationalPiiResult,
    ConversationPiiItemResult,
    InputWarning,
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
    async def test_conversation_pii_async(self, conversations_endpoint, conversations_key): # pylint: disable=too-many-statements
        client = await self.create_client(conversations_endpoint, conversations_key)

        try:
            # Build conversation input
            entities_detected: List[NamedEntity] = []

            # ---- Build input ------------------------------------
            ml_input = MultiLanguageConversationInput(
                conversations=[
                    TextConversation(
                        id="1",
                        language="en",
                        conversation_items=[
                            TextConversationItem(id="1", participant_id="Agent_1", text="Can you provide you name?"),
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

            pii_action: AnalyzeConversationOperationAction = PiiOperationAction(
                action_content=ConversationPiiActionContent(),
                name="Conversation PII",
            )
            actions: List[AnalyzeConversationOperationAction] = [pii_action]

            operation_input = AnalyzeConversationOperationInput(
                conversation_input=ml_input,
                actions=actions,
            )

            # ---- Begin LRO ----------------------------------------------------
            poller: AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]] = (
                await client.begin_analyze_conversation_job(body=operation_input)
            )

            # Operation metadata is available immediately
            print(f"Operation ID: {poller.details.get('operation_id')}")

            # Wait for completion; result is AsyncItemPaged[ConversationActions]
            paged_actions: AsyncItemPaged[ConversationActions] = await poller.result()

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

            # ---- Iterate pages and action results ----------------------------
            async for actions_page in paged_actions:
                print(
                    f"Completed: {actions_page.completed}, "
                    f"In Progress: {actions_page.in_progress}, "
                    f"Failed: {actions_page.failed}, "
                    f"Total: {actions_page.total}"
                )
                for action_result in actions_page.task_results or []: # pylint: disable=too-many-nested-blocks
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

            # ---- Print errors (from final-state metadata) ---------------------
            # Print errors
            if d.get("errors"):
                print("\nErrors:")
                for err in d["errors"]:
                    err = cast(ConversationError, err)
                    print(f"  Code: {err.code} - {err.message}")

            # Assertions
            assert len(entities_detected) > 0, "Expected at least one PII entity."
            assert (d.get("status") or "").lower() in {"succeeded", "partiallysucceeded"}
        finally:
            await client.close()
