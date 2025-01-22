# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import pathlib
import uuid
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import ASST_AZURE, PREVIEW, GPT_4_OPENAI, configure, AZURE
from openai import AssistantEventHandler
from openai.types.beta.threads import (
    Text,
    Message,
    ImageFile,
    TextDelta,
    MessageDelta,
)
from openai.types.beta.threads import Run
from openai.types.beta.threads.runs import RunStep, ToolCall, RunStepDelta, ToolCallDelta


class EventHandler(AssistantEventHandler):
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        if delta.value:
            assert delta.value is not None
        if delta.annotations:
            for annotation in delta.annotations:
                if annotation.type == "file_citation":
                    assert annotation.index is not None
                    assert annotation.file_citation.file_id
                    assert annotation.file_citation.quote
                elif annotation.type == "file_path":
                    assert annotation.index is not None
                    assert annotation.file_path.file_id

    def on_run_step_done(self, run_step: RunStep) -> None:
        details = run_step.step_details
        if details.type == "tool_calls":
            for tool in details.tool_calls:
                if tool.type == "code_interpreter":
                    assert tool.id
                    assert tool.code_interpreter.input is not None
                elif tool.type == "function":
                    assert tool.id
                    assert tool.function.arguments is not None
                    assert tool.function.name is not None

    def on_run_step_delta(self, delta: RunStepDelta, snapshot: RunStep) -> None:
        details = delta.step_details
        if details is not None:
            if details.type == "tool_calls":
                for tool in details.tool_calls or []:
                    if tool.type == "code_interpreter" and tool.code_interpreter and tool.code_interpreter.input:
                        assert tool.index is not None
                        assert tool.code_interpreter.input is not None
            elif details.type == "message_creation":
                assert details.message_creation.message_id

    def on_run_step_created(self, run_step: RunStep):
        assert run_step.object == "thread.run.step"
        assert run_step.id
        assert run_step.type
        assert run_step.created_at
        assert run_step.assistant_id
        assert run_step.thread_id
        assert run_step.run_id
        assert run_step.status
        assert run_step.step_details

    def on_message_created(self, message: Message):
        assert message.object == "thread.message"
        assert message.id
        assert message.created_at
        assert message.attachments is not None
        assert message.status
        assert message.thread_id

    def on_message_delta(self, delta: MessageDelta, snapshot: Message):
        if delta.content:
            for content in delta.content:
                if content.type == "text":
                    assert content.index is not None
                    if content.text:
                        if content.text.value:
                            assert content.text.value is not None
                        if content.text.annotations:
                            for annotation in content.text.annotations:
                                if annotation.type == "file_citation":
                                    assert annotation.end_index is not None
                                    assert annotation.file_citation.file_id
                                    assert annotation.file_citation.quote
                                    assert annotation.start_index is not None
                                elif annotation.type == "file_path":
                                    assert annotation.end_index is not None
                                    assert annotation.file_path.file_id
                                    assert annotation.start_index is not None
                elif content.type == "image_file":
                    assert content.index is not None
                    assert content.image_file.file_id


    def on_message_done(self, message: Message):
        for msg in message.content:
            if msg.type == "image_file":
                assert msg.image_file.file_id
            if msg.type == "text":
                assert msg.text.value
                if msg.text.annotations:
                    for annotation in msg.text.annotations:
                        if annotation.type == "file_citation":
                            assert annotation.end_index is not None
                            assert annotation.file_citation.file_id
                            assert annotation.file_citation.quote
                            assert annotation.start_index is not None
                            assert annotation.text is not None
                        elif annotation.type == "file_path":
                            assert annotation.end_index is not None
                            assert annotation.file_path.file_id
                            assert annotation.start_index is not None
                            assert annotation.text is not None

    def on_text_created(self, text: Text):
        assert text.value is not None

    def on_text_done(self, text: Text):
        assert text.value is not None
        for annotation in text.annotations:
            if annotation.type == "file_citation":
                assert annotation.end_index is not None
                assert annotation.file_citation.file_id
                assert annotation.file_citation.quote
                assert annotation.start_index is not None
                assert annotation.text is not None
            elif annotation.type == "file_path":
                assert annotation.end_index is not None
                assert annotation.file_path.file_id
                assert annotation.start_index is not None
                assert annotation.text is not None

    def on_image_file_done(self, image_file: ImageFile):
        assert image_file.file_id

    def on_tool_call_created(self, tool_call: ToolCall):
        assert tool_call.id

    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall):
        if delta.type == "code_interpreter":
            assert delta.index is not None
            if delta.code_interpreter:
                if delta.code_interpreter.input:
                    assert delta.code_interpreter.input is not None
            if delta.code_interpreter.outputs:
                for output in delta.code_interpreter.outputs:
                    if output.type == "image":
                        assert output.image.file_id
                    elif output.type == "logs":
                        assert output.logs
        if delta.type == "function":
            assert delta.id
            if delta.function:
                assert delta.function.arguments is not None
                assert delta.function.name is not None

    def on_tool_call_done(self, tool_call: ToolCall):
        if tool_call.type == "code_interpreter":
            assert tool_call.id
            assert tool_call.code_interpreter.input is not None
            for output in tool_call.code_interpreter.outputs:
                if output.type == "image":
                    assert output.image.file_id
                elif output.type == "logs":
                    assert output.logs
        if tool_call.type == "function":
            assert tool_call.id
            assert tool_call.function.arguments is not None
            assert tool_call.function.name is not None


@pytest.mark.live_test_only
class TestAssistants(AzureRecordedTestCase):

    def handle_run_failure(self, run: Run):
        if run.status == "failed":
            if "Rate limit" in run.last_error.message:
                pytest.skip("Skipping - Rate limit reached.")
            raise openai.OpenAIError(run.last_error.message)
        if run.status not in ["completed", "requires_action"]:
            raise openai.OpenAIError(f"Run in unexpected status: {run.status}")

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(ASST_AZURE, PREVIEW)]
    )
    def test_assistants_crud(self, client, api_type, api_version, **kwargs):

        try:
            assistant = client.beta.assistants.create(
                name="python test",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4-1106-preview",
            )
            retrieved_assistant = client.beta.assistants.retrieve(
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
            assert retrieved_assistant.object == assistant.object

            list_assistants = client.beta.assistants.list()
            for asst in list_assistants:
                assert asst.id

            modify_assistant = client.beta.assistants.update(
                assistant_id=assistant.id,
                metadata={"key": "value"}
            )
            assert modify_assistant.metadata == {"key": "value"}
        finally:
            delete_assistant = client.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_threads_crud(self, client, api_type, api_version, **kwargs):
        try:
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "I need help with math homework",
                    }
                ],
                metadata={"key": "value"},
            )
            retrieved_thread = client.beta.threads.retrieve(
                thread_id=thread.id,
            )
            assert retrieved_thread.id == thread.id
            assert retrieved_thread.object == thread.object
            assert retrieved_thread.created_at == thread.created_at
            assert retrieved_thread.metadata == thread.metadata

            updated_thread = client.beta.threads.update(
                thread_id=thread.id,
                metadata={"key": "updated"}
            )
            assert updated_thread.metadata == {"key": "updated"}

        finally:
            delete_thread = client.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_messages_crud(self, client, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file = client.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        try:
            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": "I need help with math homework",
                    }
                ],
                metadata={"key": "value"},
            )

            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="what is 2+2?",
                metadata={"math": "addition"},
                attachments=[
                    {
                        "file_id": file.id,
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            )
            retrieved_message = client.beta.threads.messages.retrieve(
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

            list_messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            for msg in list_messages:
                assert msg.id

            modify_message = client.beta.threads.messages.update(
                thread_id=thread.id,
                message_id=message.id,
                metadata={"math": "updated"}
            )
            assert modify_message.metadata == {"math": "updated"}

        finally:
            os.remove(path)
            delete_thread = client.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True
            delete_file = client.files.delete(file.id)
            assert delete_file.deleted is True

    @pytest.mark.skip("Entra ID auth not supported yet")
    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_vector_stores_crud(self, client, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file = client.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )

        try:
            vector_store = client.beta.vector_stores.create(
                name="Support FAQ"
            )
            assert vector_store.name == "Support FAQ"
            assert vector_store.id
            assert vector_store.object == "vector_store"
            assert vector_store.created_at
            assert vector_store.file_counts.total == 0

            vectors = client.beta.vector_stores.list()
            for vector in vectors:
                assert vector.id
                assert vector_store.object == "vector_store"
                assert vector_store.created_at

            vector_store = client.beta.vector_stores.update(
                vector_store_id=vector_store.id,
                name="Support FAQ and more",
                metadata={"Q": "A"}
            )
            retrieved_vector = client.beta.vector_stores.retrieve(
                vector_store_id=vector_store.id
            )
            assert retrieved_vector.id == vector_store.id
            assert retrieved_vector.name == "Support FAQ and more"
            assert retrieved_vector.metadata == {"Q": "A"}

            vector_store_file = client.beta.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=file.id
            )
            assert vector_store_file.id
            assert vector_store_file.object == "vector_store.file"
            assert vector_store_file.created_at
            assert vector_store_file.vector_store_id == vector_store.id

            vector_store_files = client.beta.vector_stores.files.list(
                vector_store_id=vector_store.id
            )
            for vector_file in vector_store_files:
                assert vector_file.id
                assert vector_file.object == "vector_store.file"
                assert vector_store_file.created_at
                assert vector_store_file.vector_store_id == vector_store.id

            vector_store_file_2 = client.beta.vector_stores.files.retrieve(
                vector_store_id=vector_store.id,
                file_id=file.id
            )
            assert vector_store_file_2.id == vector_store_file.id
            assert vector_store_file.vector_store_id == vector_store.id

        finally:
            os.remove(path)
            deleted_vector_store_file = client.beta.vector_stores.files.delete(
                vector_store_id=vector_store.id,
                file_id=file.id
            )
            assert deleted_vector_store_file.deleted is True
            deleted_vector_store = client.beta.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @pytest.mark.skip("Entra ID auth not supported yet")
    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_vector_stores_batch_crud(self, client, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        file_name_2 = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("test")

        path = pathlib.Path(file_name)

        file = client.files.create(
            file=open(path, "rb"),
            purpose="assistants"
        )
        with open(file_name_2, "w") as f:
            f.write("test")
        path_2 = pathlib.Path(file_name_2)

        file_2 = client.files.create(
            file=open(path_2, "rb"),
            purpose="assistants"
        )
        try:
            vector_store = client.beta.vector_stores.create(
                name="Support FAQ"
            )
            vector_store_file_batch = client.beta.vector_stores.file_batches.create(
                vector_store_id=vector_store.id,
                file_ids=[file.id, file_2.id]
            )
            assert vector_store_file_batch.id
            assert vector_store_file_batch.object == "vector_store.file_batch"
            assert vector_store_file_batch.created_at
            assert vector_store_file_batch.status

            vectors = client.beta.vector_stores.file_batches.list_files(
                vector_store_id=vector_store.id,
                batch_id=vector_store_file_batch.id
            )
            for vector in vectors:
                assert vector.id
                assert vector.object == "vector_store.file"
                assert vector.created_at

            retrieved_vector_store_file_batch = client.beta.vector_stores.file_batches.retrieve(
                vector_store_id=vector_store.id,
                batch_id=vector_store_file_batch.id
            )
            assert retrieved_vector_store_file_batch.id == vector_store_file_batch.id

        finally:
            os.remove(path)
            os.remove(path_2)
            delete_file = client.files.delete(file.id)
            assert delete_file.deleted is True
            delete_file = client.files.delete(file_2.id)
            assert delete_file.deleted is True
            deleted_vector_store = client.beta.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_runs_code(self, client, api_type, api_version, **kwargs):
        try:
            assistant = client.beta.assistants.create(
                name="python test",
                instructions="You are a personal math tutor. Write and run code to answer math questions.",
                tools=[{"type": "code_interpreter"}],
                model="gpt-4-1106-preview",
            )

            thread = client.beta.threads.create()

            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
            )

            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="Please address the user as Jane Doe.",
                additional_instructions="After solving each equation, say 'Isn't math fun?'",
            )
            self.handle_run_failure(run)
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)

                for message in messages:
                    assert message.content[0].type == "text"
                    assert message.content[0].text.value

            run = client.beta.threads.runs.update(
                thread_id=thread.id,
                run_id=run.id,
                metadata={"user": "user123"}
            )
            assert run.metadata == {"user": "user123"}

        finally:
            delete_assistant = client.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = client.beta.threads.delete(
                thread_id=thread.id
            )
            assert delete_thread.id == thread.id
            assert delete_thread.deleted is True

    @pytest.mark.skip("Entra ID auth not supported yet")
    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_runs_file_search(self, client, api_type, api_version, **kwargs):
        file_name = f"test{uuid.uuid4()}.txt"
        with open(file_name, "w") as f:
            f.write("Contoso company policy requires that all employees take at least 10 vacation days a year.")

        path = pathlib.Path(file_name)

        try:
            vector_store = client.beta.vector_stores.create(
                name="Support FAQ"
            )
            client.beta.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=path
            )
            assistant = client.beta.assistants.create(
                name="python test",
                instructions="You help answer questions about Contoso company policy.",
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store.id]
                    }
                },
                model="gpt-4-1106-preview"
            )

            run = client.beta.threads.create_and_run_poll(
                assistant_id=assistant.id,
                thread={
                    "messages": [
                        {"role": "user", "content": "How many vacation days am I required to take as a Contoso employee?"}
                    ]
                }
            )
            self.handle_run_failure(run)
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=run.thread_id)

                for message in messages:
                    assert message.content[0].type == "text"
                    assert message.content[0].text.value

        finally:
            os.remove(path)
            delete_assistant = client.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = client.beta.threads.delete(
                thread_id=run.thread_id
            )
            assert delete_thread.id
            assert delete_thread.deleted is True
            deleted_vector_store = client.beta.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_runs_functions(self, client, api_type, api_version, **kwargs):
        try:
            assistant = client.beta.assistants.create(
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
                model="gpt-4-1106-preview",
            )

            run = client.beta.threads.create_and_run_poll(
                assistant_id=assistant.id,
                thread={
                    "messages": [
                        {"role": "user", "content": "How's the weather in Seattle?"}
                    ]
                }
            )
            self.handle_run_failure(run)
            if run.status == "requires_action":
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=run.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": "{\"temperature\": \"22\", \"unit\": \"celsius\", \"description\": \"Sunny\"}"
                        }
                    ]
                )
            self.handle_run_failure(run)
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=run.thread_id)

                for message in messages:
                    assert message.content[0].type == "text"
                    assert message.content[0].text.value

            runs = client.beta.threads.runs.list(thread_id=run.thread_id)
            for r in runs:
                assert r.id == run.id
                assert r.thread_id == run.thread_id
                assert r.assistant_id == run.assistant_id
                assert r.created_at == run.created_at
                assert r.instructions == run.instructions
                assert r.tools == run.tools
                assert r.metadata == run.metadata

                run_steps = client.beta.threads.runs.steps.list(
                    thread_id=run.thread_id,
                    run_id=r.id
                )
                for step in run_steps:
                    assert step.id

                retrieved_step = client.beta.threads.runs.steps.retrieve(
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
            delete_assistant = client.beta.assistants.delete(
                assistant_id=assistant.id
            )
            assert delete_assistant.id == assistant.id
            assert delete_assistant.deleted is True

            delete_thread = client.beta.threads.delete(
                thread_id=run.thread_id
            )
            assert delete_thread.id
            assert delete_thread.deleted is True

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_streaming(self, client, api_type, api_version, **kwargs):
        assistant = client.beta.assistants.create(
            name="Math Tutor",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview",
        )
        try:
            thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
            )
            stream = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                stream=True,
            )

            for event in stream:
                assert event
        finally:
            client.beta.assistants.delete(assistant.id)

    @configure
    @pytest.mark.parametrize("api_type, api_version", [(ASST_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")])
    def test_assistants_stream_event_handler(self, client, api_type, api_version, **kwargs):
        assistant = client.beta.assistants.create(
            name="Math Tutor",
            instructions="You are a personal math tutor. Write and run code to answer math questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview"
        )

        try:
            question = "I need to solve the equation `3x + 11 = 14`. Can you help me and then generate an image with the answer?"

            thread = client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    },
                ]
            )

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="Please address the user as Jane Doe. The user has a premium account.",
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
        finally:
            client.beta.assistants.delete(assistant.id)
