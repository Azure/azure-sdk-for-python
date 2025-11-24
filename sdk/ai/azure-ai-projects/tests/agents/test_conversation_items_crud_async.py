# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer, recorded_by_proxy_httpx
from azure.ai.projects.models import (
    #    ResponsesUserMessageItemParam,
    #    ResponsesSystemMessageItemParam,
    #    ItemContentInputText,
    ItemType,
    ResponsesMessageRole,
    ItemContentType,
)


# TODO: Emitter did not produce the output class OpenAI.ConversationResource. Validating service response as Dict for now.
class TestConversationItemsCrudAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async_httpx
    async def test_conversation_items_crud_async(self, **kwargs):

        client = await self.create_async_client(operation_group="agents", **kwargs).get_openai_client()

        # Create a conversation to work with
        conversation = await client.conversations.create()
        print(f"Created conversation (id: {conversation.id})")

        try:
            print(f"Test create_items")
            # Create items with short-form and long-form text message as Dict
            # See https://platform.openai.com/docs/api-reference/conversations/create-items
            items = [
                {"type": "message", "role": "user", "content": "first message"},
                {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "second message"}]},
            ]
            items = await client.conversations.items.create(
                conversation.id,
                items=items,
            )
            assert items.has_more is False
            item_list = items.data
            print(f"Created item with short-form and long form text messages as Dict")
            assert len(item_list) == 2
            self._validate_conversation_item(
                item_list[0],
                expected_type=ItemType.MESSAGE,
                expected_role=ResponsesMessageRole.USER,
                expected_content_type=ItemContentType.INPUT_TEXT,
                expected_content_text="first message",
            )
            self._validate_conversation_item(
                item_list[1],
                expected_type=ItemType.MESSAGE,
                expected_role=ResponsesMessageRole.USER,
                expected_content_type=ItemContentType.INPUT_TEXT,
                expected_content_text="second message",
            )
            item1_id = item_list[0].id
            item2_id = item_list[1].id

            # Create 2 items, one system message with short-form strongly typed, and user message with long-form strongly typed
            # items = await client.conversations.items.create(
            #     conversation.id,
            #     items=[
            #         ResponsesSystemMessageItemParam(content="third message"),
            #         ResponsesUserMessageItemParam(content=[ItemContentInputText(text="fourth message")]),
            #     ],
            # )
            # assert items.has_more is False
            # item_list = items.data
            # print(f"Created 2 strongly typed items")
            # assert len(item_list) == 2
            # self._validate_conversation_item(
            #     item_list[0],
            #     expected_type=ItemType.MESSAGE,
            #     expected_role=ResponsesMessageRole.SYSTEM,
            #     expected_content_type=ItemContentType.INPUT_TEXT,
            #     expected_content_text="third message",
            # )
            # self._validate_conversation_item(
            #     item_list[1],
            #     expected_type=ItemType.MESSAGE,
            #     expected_role=ResponsesMessageRole.USER,
            #     expected_content_type=ItemContentType.INPUT_TEXT,
            #     expected_content_text="fourth message",
            # )
            # item3_id = item_list[0].id
            # item4_id = item_list[1].id

            print(f"Test retrieve item")
            item = await client.conversations.items.retrieve(conversation_id=conversation.id, item_id=item1_id)
            self._validate_conversation_item(
                item,
                expected_type=ItemType.MESSAGE,
                expected_id=item1_id,
                expected_role=ResponsesMessageRole.USER,
                expected_content_type=ItemContentType.INPUT_TEXT,
                expected_content_text="first message",
            )

            print(f"Test list items")
            item_count = 0
            async for item in client.conversations.items.list(conversation.id):
                item_count += 1
                self._validate_conversation_item(item)
            assert item_count == 2

            print(f"Test delete item")
            # result = await client.conversations.items.delete(conversation_id=conversation.id, item_id=item4_id)
            # assert result.id == conversation.id
            result = await client.conversations.items.delete(conversation_id=conversation.id, item_id=item2_id)
            assert result.id == conversation.id

            # Verify items were deleted by listing again
            remaining_items = [item async for item in client.conversations.items.list(conversation.id)]
            assert len(remaining_items) == 1

        finally:
            # Clean up the conversation
            conversation_result = await client.conversations.delete(conversation.id)
            print(f"Conversation deleted (id: {conversation_result.id}, deleted: {conversation_result.deleted})")
