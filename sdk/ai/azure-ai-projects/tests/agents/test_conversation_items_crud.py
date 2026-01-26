# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    #    ResponsesUserMessageItemParam,
    #    ResponsesSystemMessageItemParam,
    #   ItemContentInputText,
    ItemType,
)


class TestConversationItemsCrud(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.HTTPX)
    def test_conversation_items_crud(self, **kwargs):
        """
        Test CRUD operations for Conversation Items.

        This test gets an OpenAI client, creates a conversation, then performs CRUD
        operations on items within it:
        - create_items: Add items to the conversation
        - list_items: List all items in the conversation
        - delete_item: Delete specific items from the conversation

        It uses different ways of creating items: strongly typed or dictionary.

        Routes used in this test:

        Action REST API Route                                          OpenAI Client Method
        ------+-------------------------------------------------------+-----------------------------------
        POST   /openai/conversations                                   client.conversations.create()
        POST   /openai/conversations/{conversation_id}/items           client.conversations.items.create()
        GET    /openai/conversations/{conversation_id}/items/{item_id} client.conversations.items.retrieve()
        GET    /openai/conversations/{conversation_id}/items           client.conversations.items.list()
        DELETE /openai/conversations/{conversation_id}/items/{item_id} client.conversations.items.delete()
        DELETE /openai/conversations/{conversation_id}                 client.conversations.delete()
        """

        with self.create_client(operation_group="agents", **kwargs).get_openai_client() as client:

            # Create a conversation to work with
            conversation = client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")

            try:
                print(f"Test create_items")
                # Create items with short-form and long-form text message as Dict
                # See https://platform.openai.com/docs/api-reference/conversations/create-items
                items = [
                    {"type": "message", "role": "user", "content": "first message"},
                    {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "second message"}]},
                ]
                items = client.conversations.items.create(
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
                    expected_role="user",
                    expected_content_type="input_text",
                    expected_content_text="first message",
                )
                self._validate_conversation_item(
                    item_list[1],
                    expected_type=ItemType.MESSAGE,
                    expected_role="user",
                    expected_content_type="input_text",
                    expected_content_text="second message",
                )
                item1_id = item_list[0].id
                item2_id = item_list[1].id

                # Create 2 items, one system message with short-form strongly typed, and user message with long-form strongly typed
                # items = client.conversations.items.create(
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
                item = client.conversations.items.retrieve(conversation_id=conversation.id, item_id=item1_id)
                self._validate_conversation_item(
                    item,
                    expected_type=ItemType.MESSAGE,
                    expected_id=item1_id,
                    expected_role="user",
                    expected_content_type="input_text",
                    expected_content_text="first message",
                )

                print(f"Test list items")
                item_count = 0
                for item in client.conversations.items.list(conversation.id):
                    item_count += 1
                    self._validate_conversation_item(item)
                assert item_count == 2

                print(f"Test delete item")
                # result = client.conversations.items.delete(conversation_id=conversation.id, item_id=item4_id)
                # assert result.id == conversation.id
                result = client.conversations.items.delete(conversation_id=conversation.id, item_id=item2_id)
                assert result.id == conversation.id

                # Verify items were deleted by listing again
                remaining_items = list(client.conversations.items.list(conversation.id))
                assert len(remaining_items) == 1

            finally:
                # Clean up the conversation
                conversation_result = client.conversations.delete(conversation.id)
                print(f"Conversation deleted (id: {conversation_result.id}, deleted: {conversation_result.deleted})")
