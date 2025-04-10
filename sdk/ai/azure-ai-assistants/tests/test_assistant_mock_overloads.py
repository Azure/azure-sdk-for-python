from unittest.mock import patch

import pytest
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.aio import AssistantsClient as AsyncAssistantsClient
from typing import List, Dict, MutableMapping, Any

from overload_assert_utils import (
    assert_same_http_requests,
    OverloadAssertion,
    dict_to_io_bytes,
    get_mock_fn,
)

from azure.ai.assistants.models import ThreadMessageOptions, ToolResources, VectorStore


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class TestSignatures:

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_assistant(
        self, assistant: AssistantsClient, async_assistant: AsyncAssistantsClient, assertion: OverloadAssertion
    ):
        model = "gpt-4-1106-preview"
        name = "first"
        instructions = "You are a helpful assistant"
        body = {"model": model, "name": name, "instructions": instructions}

        assistant.create_assistant(model=model, name=name, instructions=instructions)
        assistant.create_assistant(body=body)
        assistant.create_assistant(body=dict_to_io_bytes(body))

        await async_assistant.create_assistant(model=model, name=name, instructions=instructions)
        await async_assistant.create_assistant(body=body)
        await async_assistant.create_assistant(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_vector_store_and_poll(
        self, assistant: AssistantsClient, async_assistant: AsyncAssistantsClient, assertion: OverloadAssertion
    ):
        file_ids = ["file_id"]
        body = {"file_ids": file_ids}

        with patch(
            "azure.ai.assistants._operations.AssistantsClientOperationsMixin.create_vector_store",
            wraps=get_mock_fn(
                assistant.create_vector_store, return_val=VectorStore({"id": "store_1", "status": "in_progress"})
            ),
        ), patch(
            "azure.ai.assistants._operations.AssistantsClientOperationsMixin.get_vector_store",
            wraps=get_mock_fn(assistant.get_vector_store, return_val=VectorStore({"id": "store_1", "status": "completed"})),
        ):

            assistant.create_vector_store_and_poll(file_ids=file_ids, sleep_interval=0)
            assistant.create_vector_store_and_poll(body=body, sleep_interval=0)
            assistant.create_vector_store_and_poll(body=dict_to_io_bytes(body), sleep_interval=0)

        with patch(
            "azure.ai.assistants.aio._operations.AssistantsClientOperationsMixin.create_vector_store",
            wraps=get_mock_fn(
                async_assistant.create_vector_store, return_val=VectorStore({"id": "store_1", "status": "in_progress"})
            ),
        ), patch(
            "azure.ai.assistants.aio._operations.AssistantsClientOperationsMixin.get_vector_store",
            wraps=get_mock_fn(
                async_assistant.get_vector_store, return_val=VectorStore({"id": "store_1", "status": "completed"})
            ),
        ):
            await async_assistant.create_vector_store_and_poll(file_ids=file_ids, sleep_interval=0)
            await async_assistant.create_vector_store_and_poll(body=body, sleep_interval=0)
            await async_assistant.create_vector_store_and_poll(body=dict_to_io_bytes(body), sleep_interval=0)
        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=2)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_thread(
        self, assistant: AssistantsClient, async_assistant: AsyncAssistantsClient, assertion: OverloadAssertion
    ):
        messages: List[ThreadMessageOptions] = []
        tool_resources: ToolResources = ToolResources()
        metadata: Dict[str, str] = {}
        body = {"messages": messages, "tool_resources": tool_resources, "metadata": metadata}

        assistant.create_thread(messages=messages, tool_resources=tool_resources, metadata=metadata)
        assistant.create_thread(body=body)
        assistant.create_thread(body=dict_to_io_bytes(body))

        await async_assistant.create_thread(messages=messages, tool_resources=tool_resources, metadata=metadata)
        await async_assistant.create_thread(body=body)
        await async_assistant.create_thread(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=False")
    @assert_same_http_requests
    async def test_create_run(
        self, assistant: AssistantsClient, async_assistant: AsyncAssistantsClient, assertion: OverloadAssertion
    ):
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        body = {"assistant_id": assistant_id}

        assistant.create_run(thread_id, assistant_id=assistant_id)
        assistant.create_run(thread_id, body=body)
        assistant.create_run(thread_id, body=dict_to_io_bytes(body))

        await async_assistant.create_run(thread_id, assistant_id=assistant_id)
        await async_assistant.create_run(thread_id, body=body)
        await async_assistant.create_run(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=True")
    @assert_same_http_requests
    async def test_create_stream(
        self, assistant: AssistantsClient, async_assistant: AsyncAssistantsClient, assertion: OverloadAssertion
    ):
        thread_id = "thread_id"
        assistant_id = "assistant_id"
        body = {"assistant_id": assistant_id}

        assistant.create_stream(thread_id, assistant_id=assistant_id)
        assistant.create_stream(thread_id, body=body)
        assistant.create_stream(thread_id, body=dict_to_io_bytes(body))

        await async_assistant.create_stream(thread_id, assistant_id=assistant_id)
        await async_assistant.create_stream(thread_id, body=body)
        await async_assistant.create_stream(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)
