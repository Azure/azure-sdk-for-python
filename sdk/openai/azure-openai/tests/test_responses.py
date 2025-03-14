# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from __future__ import annotations

import uuid
import pathlib
import os
import json

import pytest
import openai

from devtools_testutils import AzureRecordedTestCase
from conftest import (
    CUA_AZURE,
    OPENAI,
    configure,
    PREVIEW,
)


@pytest.mark.live_test_only
class TestResponses(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        response = client.responses.create(
            input="Hello, how are you?",
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
        assert response.output[0].content[0].type == "output_text"
        assert response.output[0].content[0].text
        assert response.output[0].id is not None
        assert response.output[0].role == "assistant"
        assert response.output[0].type == "message"

        retrieved_response = client.responses.retrieve(response.id)
        assert retrieved_response.id == response.id

        input_items = client.responses.input_items.list(response.id)
        assert len(input_items.data) > 0
        data = input_items.data[0]
        assert data.content[0].type == "input_text"
        assert data.content[0].text == "Hello, how are you?"
        assert data.id is not None
        assert data.role == "user"
        assert data.type == "message"

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_streaming(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        stream = client.responses.create(
            input="Count from 1 to 5",
            stream=True,
            **kwargs,
        )

        for chunk in stream:
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

    @pytest.mark.skip("Not working yet")
    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_with_computer_use_tool(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        try:
            path = pathlib.Path(__file__).parent / "assets" / "browser_github_screenshot.png"
            # with open(str(path), "rb") as f:
            #     file_data = f.read()
            
            # file = client.files.create(
            #     file=file_data,
            #     purpose="user_data"
            # )
            import base64
            with open(str(path), "rb") as f:
                data = f.read()

            base64_string = base64.b64encode(data).decode("utf-8")

            response = client.responses.create(
                input=[
                    {
                        "role": "user",
                        "content": "Where should I click to see Issues?"
                    },
                    {
                        # "type": "input_file",
                        # "file_id": file.id,
                        "type": "input_file",
                        "filename": "browser_github_screenshot.png",
                        "file_data": f"data:application/pdf;base64,{base64_string}",
                    },
                ],
                tools=[
                    {
                        "type": "computer_use_preview",
                        "environment": "browser",
                        "display_width": 1920,
                        "display_height": 1080,
                    }
                ],
                model="computer-use-preview"
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
        finally:
            # client.files.delete(file.id)
            pass

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_with_file_search_tool(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        try:
            file_name = f"test{uuid.uuid4()}.txt"
            with open(file_name, "w") as f:
                f.write("Contoso company policy requires that all employees take at least 10 vacation days a year.")

            path = pathlib.Path(file_name)

            vector_store = client.vector_stores.create(
                name="Support FAQ"
            )
            client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=path
            )
        
            response = client.responses.create(
                input="How many vacation days am I required to take as a Contoso employee?",
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": [vector_store.id]}],
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
            assert response.output[0].id is not None
            assert response.output[1].id is not None
            assert response.output[1].role == "assistant"
            assert response.output[1].type == "message"
            assert response.output[1].content[0].type == "output_text"
            assert response.output[1].content[0].text
            assert response.output[1].content[0].annotations
            assert response.output[1].content[0].annotations[0].type == "file_citations"
            assert response.output[1].content[0].annotations[0].index is not None
            assert response.output[1].content[0].annotations[0].file_id is not None
            assert response.text.format.type == "text"
            assert response.tools
            tools = response.tools[0]
            assert tools.type == "file_search"
            assert tools.vector_store_ids == [vector_store.id]

        finally:
            os.remove(path)
            deleted_vector_store = client.vector_stores.delete(
                vector_store_id=vector_store.id
            )
            assert deleted_vector_store.deleted is True

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_with_function_tool(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
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
        response = client.responses.create(
            input=messages,
            tools=tools,
            model="gpt-4o-mini",
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
        response_2 = client.responses.create(
            input=messages,
            tools=tools,
            model="gpt-4o-mini"
        )
        assert "Seattle" in response_2.output_text
        assert "80" in response_2.output_text

    @pytest.mark.skip("Not working yet")
    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_with_web_search_tool(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        response = client.responses.create(
            input="What is the weather like in seattle today? search for weather data.",
            tools=[
                {
                    "type": "web_search",
                }
            ],
            model="gpt-4o-mini",
        )

    @pytest.mark.skip("Not working yet")
    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_with_tool_choice(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        response = client.responses.create(
            model="computer-use-preview",
            input="Search for recent weather data",
            tools=[{"type": "web_search"}],
            tool_choice={"type": "web_search"}
        )
        
        assert response.tool_choice is not None
        assert response.tool_choice.type == "web_search"
        assert response.tools is not None

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_metadata(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        metadata = {"session_id": "test-123", "user_id": "user-456"}
        response = client.responses.create(
            input="Test with metadata",
            metadata=metadata,
            **kwargs,
        )
        
        assert response.metadata == metadata

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_previous_response_id(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        initial_response = client.responses.create(
            model="gpt-4o-mini",
            input="tell me a joke",
        )

        response = client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=initial_response.id,
            input=[{"role": "user", "content": "explain why this is funny."}],
        )
        assert response.previous_response_id == initial_response.id
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
        assert response.output[0].content[0].type == "output_text"
        assert response.output[0].content[0].text
        assert response.output[0].id is not None
        assert response.output[0].role == "assistant"
        assert response.output[0].type == "message"

    @pytest.mark.skip("Not working yet")
    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(CUA_AZURE, "2025-03-01-preview"), (OPENAI, "v1")]
    )
    def test_responses_structured_outputs(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):

        response = client.responses.create(
            model="gpt-4o-mini",
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
            }
        )

        event = json.loads(response.output_text)
