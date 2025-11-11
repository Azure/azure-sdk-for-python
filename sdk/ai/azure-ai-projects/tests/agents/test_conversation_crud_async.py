# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording

# from azure.ai.projects.models import ResponsesUserMessageItemParam, ItemContentInputText


class TestConversationCrudAsync(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    async def test_conversation_crud_async(self, **kwargs):

        client = await self.create_async_client(operation_group="agents", **kwargs).get_openai_client()

        async with client:
            # Create a conversations with no messages
            # See https://platform.openai.com/docs/api-reference/conversations/create
            conversation1 = await client.conversations.create()
            TestBase._validate_conversation(conversation1)
            print(f"Created conversation 1 (id: {conversation1.id})")

            # Create a conversation with a short-form text and long form messages as Dict
            conversation2 = await client.conversations.create(
                items=[
                    {"type": "message", "role": "user", "content": "first message"},
                    {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "second message"}]},
                ]
            )
            TestBase._validate_conversation(conversation2)
            print(f"Created conversation 2 (id: {conversation2.id})")

            # Create a conversation with a short-form text message, strongly typed.
            # NOTE: The assert below will fail if you just use the auto-emitted source code as-is. You need to apply
            # the fixes in file post-emitter-fixes.cmd to fix the emitted code and make the assert below pass.
            # conversation3 = await client.conversations.create(
            #     items=[
            #         ResponsesUserMessageItemParam(content="third message"),
            #         ResponsesUserMessageItemParam(content=[ItemContentInputText(text="fourth message")]),
            #     ]
            # )
            # TestBase._validate_conversation(conversation3)
            # print(f"Created conversation 3 (id: {conversation3.id})")

            # Get first conversation
            conversation = await client.conversations.retrieve(conversation_id=conversation1.id)
            TestBase._validate_conversation(conversation1, expected_id=conversation1.id)
            print(f"Got conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # List conversations
            # Commented out because OpenAI client does not support listing conversations
            # for conversation in client.conversations.list():
            #     TestBase._validate_conversation(conversation)
            #     print(f"Listed conversation (id: {conversation.id})")

            # Update conversation
            metadata = {"key1": "value1", "key2": "value2"}
            conversation = await client.conversations.update(conversation_id=conversation1.id, metadata=metadata)
            TestBase._validate_conversation(conversation, expected_id=conversation1.id, expected_metadata=metadata)
            print(f"Conversation updated")

            conversation = await client.conversations.retrieve(conversation_id=conversation1.id)
            TestBase._validate_conversation(conversation)
            print(f"Got updated conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # Delete conversation
            # result = await client.conversations.delete(conversation_id=conversation3.id)
            # assert result.id == conversation3.id
            # assert result.deleted
            # print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")
            result = await client.conversations.delete(conversation_id=conversation2.id)
            assert result.id == conversation2.id
            assert result.deleted
            print(f"Conversation 2 deleted (id: {result.id}, deleted: {result.deleted})")
            result = await client.conversations.delete(conversation_id=conversation1.id)
            assert result.id == conversation1.id
            assert result.deleted
            print(f"Conversation 1 deleted (id: {result.id}, deleted: {result.deleted})")
