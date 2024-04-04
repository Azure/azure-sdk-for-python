# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import time
import pytest
import pathlib
import uuid
from devtools_testutils import AzureRecordedTestCase
from conftest import ASST_AZURE, ASST_AZUREAD, PREVIEW, GPT_4_OPENAI, configure_async

TIMEOUT = 300

class TestAssistantsAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(ASST_AZURE, PREVIEW), (ASST_AZUREAD, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_assistants_crud(self, client_async, api_type, api_version, **kwargs):
        try:
            assistant = await client_async.beta.assistants.create(
                name="python test",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                **kwargs,
            )
            retrieved_assistant = await client_async.beta.assistants.retrieve(
                assistant_id=assistant.id,
            )
            assert retrieved_assistant.id == assistant.id
            assert retrieved_assistant.name == assistant.name
            assert retrieved_assistant.instructions == assistant.instructions
            assert retrieved_assistant.tools == assistant.tools
            assert retrieved_assistant.model == assistant.model
            assert retrieved_assistant.created_at == assistant.created_at
            assert retrieved_assistant.description == assistant.description
            assert retrieved_assistant.metadata == assistant.metadata
            assert retrieved_assistant.file_ids == assistant.file_ids
            assert retrieved_assistant.object == assistant.object

            list_assistants = client_async.beta.assistants.list()
            async for asst in list_assistants:
                assert asst.id

            modify_assistant = await client_async.beta.assistants.update(
                assistant_id=assistant.id,
                metadata={"key": "value"}
            )
            assert modify_assistant.metadata == {"key": "value"}
        finally:
            delete_assistant = await client_async.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_files_crud(self, client_async, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file1 = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        file2 = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        try:
            assistant = await client_async.beta.assistants.create(
                name="python test",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                file_ids=[file1.id],
                **kwargs
            )
            assert assistant.file_ids == [file1.id]
            created_assistant_file = await client_async.beta.assistants.files.create(
                assistant_id=assistant.id,
                file_id=file2.id
            )

            retrieved_assistant_file = await client_async.beta.assistants.files.retrieve(
                assistant_id=assistant.id,
                file_id=file2.id
            )
            assert retrieved_assistant_file.id == created_assistant_file.id
            assert retrieved_assistant_file.object == created_assistant_file.object
            assert retrieved_assistant_file.created_at == created_assistant_file.created_at
            assert retrieved_assistant_file.assistant_id == created_assistant_file.assistant_id

            list_assistants_files = client_async.beta.assistants.files.list(
                assistant_id=assistant.id
            )
            async for asst_file in list_assistants_files:
                assert asst_file.id

            delete_assistant_file = await client_async.beta.assistants.files.delete(
                assistant_id=assistant.id,
                file_id=file2.id
            )
            assert delete_assistant_file.id == retrieved_assistant_file.id
            assert delete_assistant_file.deleted is True
        finally:
            os.remove(path)
            delete_assistant = await client_async.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_threads_crud(self, client_async, api_type, api_version, **kwargs):
        try:
            thread = await client_async.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "I need help with math homework",
                    }
                ],
                metadata={"key": "value"},
            )

            retrieved_thread = await client_async.beta.threads.retrieve(
                thread_id=thread.id,
            )
            assert retrieved_thread.id == thread.id
            assert retrieved_thread.object == thread.object
            assert retrieved_thread.created_at == thread.created_at
            assert retrieved_thread.metadata == thread.metadata

            updated_thread = await client_async.beta.threads.update(
                thread_id=thread.id,
                metadata={"key": "updated"}
            )
            assert updated_thread.metadata == {"key": "updated"}

        finally:
            delete_thread = await client_async.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_messages_crud(self, client_async, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        try:
            thread = await client_async.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "I need help with math homework",
                    }
                ],
                metadata={"key": "value"},
            )

            message = await client_async.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="what is 2+2?",
                metadata={"math": "addition"},
                file_ids=[file.id]
            )
            retrieved_message = await client_async.beta.threads.messages.retrieve(
                thread_id=thread.id,
                message_id=message.id
            )
            assert retrieved_message.id == message.id
            assert retrieved_message.created_at == message.created_at
            assert retrieved_message.metadata == message.metadata
            assert retrieved_message.object == message.object
            assert retrieved_message.thread_id == thread.id
            assert retrieved_message.role == message.role
            assert retrieved_message.content == message.content

            retrieved_message_file = await client_async.beta.threads.messages.files.retrieve(
                thread_id=thread.id,
                message_id=message.id,
                file_id=file.id
            )
            assert retrieved_message_file.id
            assert retrieved_message_file.message_id
            assert retrieved_message_file.created_at

            list_messages = client_async.beta.threads.messages.list(
                thread_id=thread.id
            )
            async for msg in list_messages:
                assert msg.id

            list_message_files = client_async.beta.threads.messages.files.list(
                thread_id=thread.id,
                message_id=message.id
            )
            async for msg_file in list_message_files:
                assert msg_file.id

            modify_message = await client_async.beta.threads.messages.update(
                thread_id=thread.id,
                message_id=message.id,
                metadata={"math": "updated"}
            )
            assert modify_message.metadata == {"math": "updated"}

        finally:
            os.remove(path)
            delete_thread = await client_async.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_runs_code(self, client_async, api_type, api_version, **kwargs):

        try:
            assistant = await client_async.beta.assistants.create(
                name="python test",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                **kwargs,
            )
            thread = await client_async.beta.threads.create()

            message = await client_async.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
            )

            run = await client_async.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="Please address the user as Jane Doe.",
                # additional_instructions="After solving each equation, say 'Isn't math fun?'",  # not supported by AOAI yet
            )

            start_time = time.time()

            while True:
                if time.time() - start_time > TIMEOUT:
                    raise TimeoutError("Run timed out")

                run = await client_async.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

                if run.status == "completed":
                    messages = client_async.beta.threads.messages.list(thread_id=thread.id)

                    async for message in messages:
                        assert message.content[0].type == "text"
                        assert message.content[0].text.value

                    break
                else:
                    time.sleep(5)

            run = await client_async.beta.threads.runs.update(
                thread_id=thread.id,
                run_id=run.id,
                metadata={"user": "user123"}
            )
            assert run.metadata == {"user": "user123"}

        finally:
            delete_assistant = await client_async.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = await client_async.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True

    @pytest.mark.skip("AOAI does not support retrieval tools yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_runs_retrieval(self, client_async, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("Contoso company policy requires that all employees take at least 10 vacation days a year.")

        path = pathlib.Path(file_name)

        file = await client_async.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )
        try:
            assistant = await client_async.beta.assistants.create(
                name="python test",
                instructions="You help answer questions about Contoso company policy.",
                tools=[{"type": "retrieval"}],
                file_ids=[file.id],
                **kwargs
            )

            run = await client_async.beta.threads.create_and_run(
                assistant_id=assistant.id,
                thread={
                    "messages": [
                        {"role": "user", "content": "How many vacation days am I required to take as a Contoso employee?"}
                    ]
                }
            )

            start_time = time.time()

            while True:
                if time.time() - start_time > TIMEOUT:
                    raise TimeoutError("Run timed out")

                run = await client_async.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)

                if run.status == "completed":
                    messages = client_async.beta.threads.messages.list(thread_id=run.thread_id)

                    async for message in messages:
                        assert message.content[0].type == "text"
                        assert message.content[0].text.value

                    break

                time.sleep(5)

        finally:
            os.remove(path)
            delete_assistant = await client_async.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = await client_async.beta.threads.delete(
                thread_id=run.thread_id
            )
            assert delete_thread.id
            assert delete_thread.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    async def test_assistants_runs_functions(self, client_async, api_type, api_version, **kwargs):
        try:
            assistant = await client_async.beta.assistants.create(
                name="python test",
                instructions="You help answer questions about the weather.",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "Get the current weather",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA",
                                    },
                                    "format": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"],
                                        "description": "The temperature unit to use. Infer this from the users location.",
                                    },
                                },
                                "required": ["location"],
                            }
                        }
                    }
                ],
                **kwargs,
            )

            run = await client_async.beta.threads.create_and_run(
                assistant_id=assistant.id,
                thread={
                    "messages": [
                        {"role": "user", "content": "How's the weather in Seattle?"}
                    ]
                }
            )
            start_time = time.time()

            while True:
                if time.time() - start_time > TIMEOUT:
                    raise TimeoutError("Run timed out")

                run = await client_async.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)

                if run.status == "requires_action":
                    run = await client_async.beta.threads.runs.submit_tool_outputs(
                        thread_id=run.thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {
                                "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                                "output": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
                            }
                        ]
                    )

                if run.status == "completed":
                    messages = client_async.beta.threads.messages.list(thread_id=run.thread_id)

                    async for message in messages:
                        assert message.content[0].type == "text"
                        assert message.content[0].text.value

                    break

                time.sleep(5)

            runs = client_async.beta.threads.runs.list(thread_id=run.thread_id)
            async for r in runs:
                assert r.id == run.id
                assert r.thread_id == run.thread_id
                assert r.assistant_id == run.assistant_id
                assert r.created_at == run.created_at
                assert r.instructions == run.instructions
                assert r.tools == run.tools
                assert r.metadata == run.metadata

                run_steps = client_async.beta.threads.runs.steps.list(
                    thread_id=run.thread_id,
                    run_id=r.id
                )
                async for step in run_steps:
                    assert step.id

                retrieved_step = await client_async.beta.threads.runs.steps.retrieve(
                    thread_id=run.thread_id,
                    run_id=r.id,
                    step_id=step.id
                )
                assert retrieved_step.id
                assert retrieved_step.created_at
                assert retrieved_step.run_id
                assert retrieved_step.thread_id
                assert retrieved_step.assistant_id
                assert retrieved_step.type
                assert retrieved_step.step_details

        finally:
            delete_assistant = await client_async.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = await client_async.beta.threads.delete(
                thread_id=run.thread_id
            )
            assert delete_thread.id
            assert delete_thread.deleted is True
