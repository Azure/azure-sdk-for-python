# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

import base64
import uuid
import pathlib
import os
import json

import pytest
import openai

from devtools_testutils import AzureRecordedTestCase
from conftest import (
    GPT_4_AZURE,
    GPT_4_OPENAI,
    configure_async,
    PREVIEW,
)

def assert_required(response: openai.types.responses.Response):
    assert response.id is not None
    assert response.created_at is not None
    assert response.model
    assert response.object == "response"
    assert response.status in ["completed", "incomplete", "failed", "in_progress"]
    assert response.usage.input_tokens is not None
    assert response.usage.output_tokens is not None
    assert response.usage.total_tokens == response.usage.input_tokens + response.usage.output_tokens
    assert response.usage.output_tokens_details is not None
    assert len(response.output) > 0
    assert response.output[0].content[0].type == "output_text"
    assert response.output[0].content[0].text
    assert response.output[0].id is not None
    assert response.output[0].role == "assistant"
    assert response.output[0].type == "message"
    assert response.parallel_tool_calls is not None
    assert response.text.format.type is not None
    # assert response.tool_choice is not None  TODO
    assert response.tools is not None


@pytest.mark.live_test_only
class TestResponsesAsync(AzureRecordedTestCase):

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        response = await client_async.responses.create(
            input="Hello, how are you?",
            **kwargs,
        )

        assert_required(response)

        retrieved_response = await client_async.responses.retrieve(response.id)
        assert_required(response)
        assert retrieved_response.id == response.id

        input_items = await client_async.responses.input_items.list(response.id)
        assert len(input_items.data) > 0
        data = input_items.data[0]
        assert data.content[0].type == "input_text"
        assert data.content[0].text == "Hello, how are you?"
        assert data.id is not None
        assert data.role == "user"
        assert data.type == "message"

        await client_async.responses.delete(response.id)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_streaming(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        stream = await client_async.responses.create(
            input="Count from 1 to 5",
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.type == "response.created":
                assert chunk.response is not None
                assert chunk.response.id is not None
                assert chunk.response.created_at is not None
                assert chunk.response.model is not None
            if chunk.type == "response.output_item.added":
                assert chunk.output_index is not None
                assert chunk.item.id is not None
                assert chunk.item.role == "assistant"
                assert chunk.item.type == "message"
            if chunk.type == "response.content_part.added":
                assert chunk.content_index is not None
                assert chunk.output_index is not None
                assert chunk.item_id is not None
                assert chunk.part.text is not None
                assert chunk.part.type == "output_text"
            if chunk.type == "response.output_text.delta":
                assert chunk.content_index is not None
                assert chunk.output_index is not None
                assert chunk.item_id is not None
                assert chunk.delta is not None
            if chunk.type == "response.output_text.done":
                assert chunk.content_index is not None
                assert chunk.output_index is not None
                assert chunk.item_id is not None
                assert chunk.text is not None
            if chunk.type == "response.content_part.done":
                assert chunk.content_index is not None
                assert chunk.output_index is not None
                assert chunk.item_id is not None
                assert chunk.part.text is not None
                assert chunk.part.type == "output_text"
            if chunk.type == "response.output_item.done":
                assert chunk.output_index is not None
                assert chunk.item.id is not None
                assert chunk.item.role == "assistant"
                assert chunk.item.type == "message"
                assert chunk.item.content[0].type == "output_text"
                assert chunk.item.content[0].text is not None
            if chunk.type == "response.completed":
                assert chunk.response is not None
                assert chunk.response.id is not None
                assert chunk.response.created_at is not None
                assert chunk.response.model is not None
                assert chunk.response.status == "completed"
                assert chunk.response.usage.input_tokens is not None
                assert chunk.response.usage.output_tokens is not None
                assert chunk.response.usage.total_tokens == chunk.response.usage.input_tokens + chunk.response.usage.output_tokens
                assert chunk.response.usage.output_tokens_details is not None

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_with_computer_use_tool(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        path = pathlib.Path(__file__).parent / "assets" / "browser_github_screenshot.png"
        with open(str(path), "rb") as f:
            data = f.read()

        base64_string = base64.b64encode(data).decode("utf-8")

        response = await client_async.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Where should I click to see Issues?"},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{base64_string}"}
                    ]
                }
            ],
            tools=[
                {
                    "type": "computer_use_preview",
                    "environment": "browser",
                    "display_width": 1920,
                    "display_height": 1080,
                }
            ],
            model="computer-use-preview",
            truncation="auto",
            include=["computer_call_output.output.image_url"]
        )

        assert response.id is not None
        assert response.created_at is not None
        assert response.model
        assert response.object == "response"
        assert response.status == "completed"
        assert response.truncation == "auto"
        assert response.output_text is not None
        assert response.usage.input_tokens is not None
        assert response.usage.output_tokens is not None
        assert response.usage.total_tokens == response.usage.input_tokens + response.usage.output_tokens
        assert response.usage.output_tokens_details is not None
        assert len(response.output) > 0
        assert response.output[0].content[0].type == "output_text"
        assert response.output[0].content[0].text
        assert response.output[0].id is not None
        assert response.output[0].role == "assistant"
        assert response.output[0].type == "message"

        assert response.tools
        tools = response.tools[0]
        assert tools.type == "computer_use_preview"
        assert tools.display_height == 1080
        assert tools.display_width == 1920
        assert tools.environment == "browser"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_with_file_search_tool(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        try:
            file_name = f"test{uuid.uuid4()}.txt"
            with open(file_name, "w") as f:
                f.write("Contoso company policy requires that all employees take at least 10 vacation days a year.")

            path = pathlib.Path(file_name)

            vector_store = await client_async.vector_stores.create(
                name="Support FAQ"
            )
            await client_async.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=path
            )
        
            response = await client_async.responses.create(
                input="How many vacation days am I required to take as a Contoso employee?",
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store.id]}],
                include=["file_search_call.results"],
                **kwargs
            )

            assert response.id is not None
            assert response.created_at is not None
            assert response.model
            assert response.object == "response"
            assert response.status == "completed"
            assert response.output_text is not None
            assert response.usage.input_tokens is not None
            assert response.usage.output_tokens is not None
            assert response.usage.total_tokens == response.usage.input_tokens + response.usage.output_tokens
            assert response.usage.output_tokens_details is not None
            assert len(response.output) > 0
            assert response.output[0].type == "file_search_call"
            assert response.output[0].status == "completed"
            assert response.output[0].queries
            assert response.output[0].results
            assert response.output[0].results[0].file_id is not None
            assert response.output[0].results[0].score is not None
            assert response.output[0].results[0].text is not None
            assert response.output[0].id is not None
            assert response.output[1].id is not None
            assert response.output[1].role == "assistant"
            assert response.output[1].type == "message"
            assert response.output[1].content[0].type == "output_text"
            assert response.output[1].content[0].text
            assert response.output[1].content[0].annotations
            assert response.output[1].content[0].annotations[0].type == "file_citation"
            assert response.output[1].content[0].annotations[0].index is not None
            assert response.output[1].content[0].annotations[0].file_id is not None
            assert response.text.format.type == "text"
            assert response.tools
            tools = response.tools[0]
            assert tools.type == "file_search"
            assert tools.vector_store_ids == [vector_store.id]
            assert tools.ranking_options

        finally:
            os.remove(path)
            deleted_vector_store = await client_async.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_with_function_tool(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        messages = [{"role": "user", "content": "What is the weather like in seattle today? search for weather data."}]
        tools = [
            {
                "type": "function",
                "name": "weather_search",
                "description": "Search for weather data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to search for weather data.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date to search for weather data.",
                        },
                    },
                    "required": ["location"],
                },

            }
        ]
        response = await client_async.responses.create(
            input=messages,
            tools=tools,
            # tool_choice={"type": "function", "name": "weather_search"}  # TODO
            **kwargs,
        )
        assert response.id is not None
        assert response.created_at is not None
        assert response.model
        assert response.object == "response"
        assert response.status == "completed"
        assert response.usage.input_tokens is not None
        assert response.usage.output_tokens is not None
        assert response.usage.total_tokens == response.usage.input_tokens + response.usage.output_tokens
        assert response.usage.output_tokens_details is not None
        assert len(response.output) > 0
        assert "Seattle" in response.output[0].arguments
        assert response.output[0].call_id is not None
        assert response.output[0].id is not None
        assert response.output[0].name == "weather_search"
        assert response.output[0].type == "function_call"

        # assert response.tool_choice.name == "weather_search"  TODO
        # assert response.tool_choice.type == "function"
        assert response.tools
        tools_response = response.tools[0]
        assert tools_response.type == "function"
        assert tools_response.name == "weather_search"
        assert tools_response.description == "Search for weather data"
        assert tools_response.parameters is not None
        messages.append(response.output[0])
        messages.append({
            "type": "function_call_output",
            "call_id": response.output[0].call_id,
            "output": "80 degrees F"
        })
        response_2 = await client_async.responses.create(
            input=messages,
            tools=tools,
            **kwargs,
        )
        assert "Seattle" in response_2.output_text
        assert "80" in response_2.output_text

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_with_parallel_tool_calls(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        messages = [
            {"role": "system", "content": "Don't make assumptions about what values to plug into tools. Ask for clarification if a user request is ambiguous."},
            {"role": "user", "content": "What's the weather like today in Seattle and Los Angeles?"}
        ]
        tools = [
            {
                "type": "function",
                "name": "weather_search",
                "description": "Search for weather data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to search for weather data.",
                        },
                        "date": {
                            "type": "string",
                            "description": "The date to search for weather data.",
                        },
                    },
                    "required": ["location"],
                },

            }
        ]
        response = await client_async.responses.create(
            input=messages,
            tools=tools,
            parallel_tool_calls=False,
            **kwargs,
        )
        assert response.parallel_tool_calls is False
        assert len(response.output) == 1
        assert response.id is not None
        assert response.created_at is not None
        assert response.model
        assert response.object == "response"
        assert response.status == "completed"
        assert response.usage.input_tokens is not None
        assert response.usage.output_tokens is not None
        assert response.usage.total_tokens == response.usage.input_tokens + response.usage.output_tokens
        assert response.usage.output_tokens_details is not None
        assert len(response.output) > 0
        assert response.output[0].call_id is not None
        assert response.output[0].id is not None
        assert response.output[0].name == "weather_search"
        assert response.output[0].type == "function_call"

        assert response.tools
        tools_response = response.tools[0]
        assert tools_response.type == "function"
        assert tools_response.name == "weather_search"
        assert tools_response.description == "Search for weather data"
        assert tools_response.parameters is not None


    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_OPENAI, "v1")]
    )
    async def test_responses_with_web_search_tool(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        response = await client_async.responses.create(
            input="What is the weather like in seattle today? search for weather data.",
            tools=[
                {
                    "type": "web_search_preview",
                    "search_context_size": "medium"

                }
            ],
            **kwargs,
        )
        assert_required(response)

        assert response.tools
        tools_response = response.tools[0]
        assert tools_response.type == "'web_search_preview'"
        assert tools_response.search_context_size == "medium"

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_metadata(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        metadata = {"session_id": "test-123", "user_id": "user-456"}
        response = await client_async.responses.create(
            input="Test with metadata",
            metadata=metadata,
            **kwargs,
        )
        assert_required(response)
        assert response.metadata == metadata

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_temperature(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        response = await client_async.responses.create(
            input="hello there!",
            temperature=0.1,
            **kwargs,
        )
        assert_required(response)
        assert response.temperature == 0.1

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_top_p(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        response = await client_async.responses.create(
            input="hello there!",
            top_p=0.1,
            **kwargs,
        )
        assert_required(response)
        assert response.top_p == 0.1

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_user(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        user = str(uuid.uuid4())
        response = await client_async.responses.create(
            input="hello there!",
            user=user,
            **kwargs,
        )
        assert_required(response)
        assert response.user == user

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_previous_response_id(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        initial_response = await client_async.responses.create(
            input="tell me a joke",
            **kwargs,
        )

        response = await client_async.responses.create(
            previous_response_id=initial_response.id,
            input=[{"role": "user", "content": "explain why this is funny."}],
            **kwargs,
        )
        assert response.previous_response_id == initial_response.id
        assert_required(response)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_store(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        response = await client_async.responses.create(
            input=[{"role": "user", "content": "write me an original happy birthday song"}],
            store=True,
            **kwargs,
        )

        assert_required(response)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_instructions(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        response = await client_async.responses.create(
            input=[{"role": "user", "content": "write me an original happy birthday song"}],
            instructions="Do as the user says, but always use Spanish for your response.",
            **kwargs,
        )

        assert response.instructions == "Do as the user says, but always use Spanish for your response."
        assert_required(response)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_max_output_tokens(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        response = await client_async.responses.create(
            input=[{"role": "user", "content": "write me an original happy birthday song. keep it short."}],
            max_output_tokens=20,
            **kwargs,
        )

        assert_required(response)
        assert response.usage.output_tokens <= 20

    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_input_url(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        response = await client_async.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "what's in this image?"},
                        {"type": "input_image", "image_url": "https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/images/handwritten-note.jpg"}
                    ]
                }
            ],
            include=["message.input_image.image_url"],
            **kwargs,
        )

        assert_required(response)

    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_input_file(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        try:
            hello_pdf = pathlib.Path(__file__).parent / "assets" / "hello_world.pdf"
            file = await client_async.files.create(
                file=open(str(hello_pdf), "rb"),
                purpose="assistants"  # should be user_data
            )

            response = await client_async.responses.create(
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "what's in this file?"},
                            {"type": "input_file", "file_id": file.id}
                        ]
                    }
                ],
                **kwargs,
            )

            assert_required(response)
        finally:
            await client_async.files.delete(file.id)

    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_input_file_base64(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        hello_pdf = pathlib.Path(__file__).parent / "assets" / "hello_world.pdf"
        with open(str(hello_pdf), "rb") as f:
            data = f.read()

        base64_string = base64.b64encode(data).decode("utf-8")

        response = await client_async.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "what's in this file?"},
                        {
                            "type": "input_file",
                            "filename": "hello_world.pdf",
                            "file_data": f"data:application/pdf;base64,{base64_string}",
                        }
                    ]
                }
            ],
            **kwargs,
        )

        assert_required(response)

    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_structured_outputs(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):

        response = await client_async.responses.create(
            input=[
                {"role": "system", "content": "Extract the event information."},
                {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "calendar_event",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string"
                            },
                            "date": {
                                "type": "string"
                            },
                            "participants": {
                                "type": "array", 
                                "items": {
                                    "type": "string"
                                }
                            },
                        },
                        "required": ["name", "date", "participants"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            **kwargs,
        )
        assert_required(response)
        event = json.loads(response.output_text)
        assert event
        assert event["name"].lower() == "science fair"
        assert event["date"].lower() == "friday"
        assert [p.lower() for p in event["participants"]] == ["alice", "bob"]
        assert response.text.format.type == "json_schema"
        assert response.text.format.name == "calendar_event"

    @pytest.mark.skip("Not working for Azure yet")
    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]
    )
    async def test_responses_json_object_outputs(self, client_async: openai.AsyncAzureOpenAI | openai.AsyncOpenAI, api_type, api_version, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020? Return in json with answer as the key."}
        ]

        response = await client_async.responses.create(input=messages, text={"format": {"type": "json_object"}}, **kwargs)
        assert_required(response)
        assert json.loads(response.output_text)
