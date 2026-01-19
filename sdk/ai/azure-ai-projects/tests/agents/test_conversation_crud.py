# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport

# from azure.ai.projects.models import ResponsesUserMessageItemParam, ItemContentInputText


# TODO: Emitter did not produce the output class OpenAI.ConversationResource. Validating service response as Dict for now.
class TestConversationCrud(TestBase):

    # To run only this test:
    # pytest tests/agents/test_conversation_crud.py::TestConversationCrud::test_conversation_crud -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.HTTPX)
    def test_conversation_crud(self, **kwargs):
        """
        Test CRUD operations for Conversations.

        This test gets an OpenAI client, creates three conversations, each with different message formats.
        It then retrieves, lists, and deletes the conversations, validating at each step.
        It uses different ways of creating conversations: strongly typed, dictionary, and IO[bytes].

        Routes used in this test:

        Action REST API Route                            OpenAI Client Method
        ------+-----------------------------------------+-----------------------------------
        POST   /openai/conversations                     client.conversations.create()
        GET    /openai/conversations                     client.conversations.list()
        GET    /openai/conversations/{conversation_id}   client.conversations.retrieve()
        POST   /openai/conversations/{conversation_id}   client.conversations.update()
        DELETE /openai/conversations/{conversation_id}   client.conversations.delete()
        """

        with self.create_client(operation_group="agents", **kwargs).get_openai_client() as client:

            # Create a conversations with no messages
            # See https://platform.openai.com/docs/api-reference/conversations/create
            conversation1 = client.conversations.create()
            TestBase._validate_conversation(conversation1)
            print(f"Created conversation 1 (id: {conversation1.id})")

            # Create a conversation with a short-form text and long form messages as Dict
            conversation2 = client.conversations.create(
                items=[
                    {"type": "message", "role": "user", "content": "first message"},
                    {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "second message"}]},
                ]
            )
            TestBase._validate_conversation(conversation2)
            print(f"Created conversation 2 (id: {conversation2.id})")

            # Create a conversation with a short-form text message, strongly typed.
            # TODO: OpenAI accepts `items: Iterable[ResponseInputItemParam] | Omit | None = omit,` but our emitted
            # code does not have any class named ResponseInputItemParam. This causes typing errors. Make sure this is fixed when
            # we emit from TypeSpec that uses the new OpenAI TypeSpec package.
            # NOTE: The assert below will fail if you just use the auto-emitted source code as-is. You need to apply
            # the fixes in file post-emitter-fixes.cmd to fix the emitted code and make the assert below pass.
            # conversation3 = client.conversations.create(
            #     items=[
            #         ResponsesUserMessageItemParam(content="third message"),
            #         ResponsesUserMessageItemParam(content=[ItemContentInputText(text="fourth message")]),
            #     ]
            # )
            # TestBase._validate_conversation(conversation3)
            # print(f"Created conversation 3 (id: {conversation3.id})")

            # Get first conversation
            conversation = client.conversations.retrieve(conversation_id=conversation1.id)
            TestBase._validate_conversation(conversation1, expected_id=conversation1.id)
            print(f"Got conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # List conversations
            # Commented out because OpenAI client does not support listing conversations
            # for conversation in client.conversations.list():
            #     TestBase._validate_conversation(conversation)
            #     print(f"Listed conversation (id: {conversation.id})")

            # Update conversation
            metadata = {"key1": "value1", "key2": "value2"}
            conversation = client.conversations.update(conversation_id=conversation1.id, metadata=metadata)
            TestBase._validate_conversation(conversation, expected_id=conversation1.id, expected_metadata=metadata)
            print(f"Conversation updated")

            conversation = client.conversations.retrieve(conversation_id=conversation1.id)
            TestBase._validate_conversation(conversation)
            print(f"Got updated conversation (id: {conversation.id}, metadata: {conversation.metadata})")

            # Delete conversation
            # result = client.conversations.delete(conversation_id=conversation3.id)
            # assert result.id == conversation3.id
            # assert result.deleted
            # print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")
            result = client.conversations.delete(conversation_id=conversation2.id)
            assert result.id == conversation2.id
            assert result.deleted
            print(f"Conversation 2 deleted (id: {result.id}, deleted: {result.deleted})")
            result = client.conversations.delete(conversation_id=conversation1.id)
            assert result.id == conversation1.id
            assert result.deleted
            print(f"Conversation 1 deleted (id: {result.id}, deleted: {result.deleted})")
