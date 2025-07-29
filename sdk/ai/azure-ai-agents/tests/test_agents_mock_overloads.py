from unittest.mock import patch

import pytest
from azure.ai.agents import AgentsClient
from azure.ai.agents.aio import AgentsClient as AsyncAgentsClient
from typing import List, Dict, MutableMapping, Any

from overload_assert_utils import (
    assert_same_http_requests,
    OverloadAssertion,
    dict_to_io_bytes,
    get_mock_fn,
)

from azure.ai.agents.models import ThreadMessageOptions, ToolResources, VectorStore


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class TestSignatures:

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_agent(
        self, agent: AgentsClient, async_agent: AsyncAgentsClient, assertion: OverloadAssertion
    ):
        model = "gpt-4-1106-preview"
        name = "first"
        instructions = "You are a helpful agent"
        body = {"model": model, "name": name, "instructions": instructions}

        agent.create_agent(model=model, name=name, instructions=instructions)
        agent.create_agent(body=body)
        agent.create_agent(body=dict_to_io_bytes(body))

        await async_agent.create_agent(model=model, name=name, instructions=instructions)
        await async_agent.create_agent(body=body)
        await async_agent.create_agent(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_vector_store_and_poll(
        self, agent: AgentsClient, async_agent: AsyncAgentsClient, assertion: OverloadAssertion
    ):
        file_ids = ["file_id"]
        body = {"file_ids": file_ids}

        with patch(
            "azure.ai.agents.operations._operations.VectorStoresOperations.create",
            wraps=get_mock_fn(
                agent.vector_stores.create, return_val=VectorStore({"id": "store_1", "status": "in_progress"})
            ),
        ), patch(
            "azure.ai.agents.operations._operations.VectorStoresOperations.get",
            wraps=get_mock_fn(
                agent.vector_stores.get, return_val=VectorStore({"id": "store_1", "status": "completed"})
            ),
        ):

            agent.vector_stores.create_and_poll(file_ids=file_ids, polling_interval=0)
            agent.vector_stores.create_and_poll(body=body, polling_interval=0)
            agent.vector_stores.create_and_poll(body=dict_to_io_bytes(body), polling_interval=0)

        with patch(
            "azure.ai.agents.aio.operations._operations.VectorStoresOperations.create",
            wraps=get_mock_fn(
                async_agent.vector_stores.create, return_val=VectorStore({"id": "store_1", "status": "in_progress"})
            ),
        ), patch(
            "azure.ai.agents.aio.operations._operations.VectorStoresOperations.get",
            wraps=get_mock_fn(
                async_agent.vector_stores.get, return_val=VectorStore({"id": "store_1", "status": "completed"})
            ),
        ):
            await async_agent.vector_stores.create_and_poll(file_ids=file_ids, polling_interval=0)
            await async_agent.vector_stores.create_and_poll(body=body, polling_interval=0)
            await async_agent.vector_stores.create_and_poll(body=dict_to_io_bytes(body), polling_interval=0)
        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=2)

    @pytest.mark.asyncio
    @assert_same_http_requests
    async def test_create_thread(
        self, agent: AgentsClient, async_agent: AsyncAgentsClient, assertion: OverloadAssertion
    ):
        messages: List[ThreadMessageOptions] = []
        tool_resources: ToolResources = ToolResources()
        metadata: Dict[str, str] = {}
        body = {"messages": messages, "tool_resources": tool_resources, "metadata": metadata}

        agent.threads.create(messages=messages, tool_resources=tool_resources, metadata=metadata)
        agent.threads.create(body=body)
        agent.threads.create(body=dict_to_io_bytes(body))

        await async_agent.threads.create(messages=messages, tool_resources=tool_resources, metadata=metadata)
        await async_agent.threads.create(body=body)
        await async_agent.threads.create(body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=False")
    @assert_same_http_requests
    async def test_create_run(self, agent: AgentsClient, async_agent: AsyncAgentsClient, assertion: OverloadAssertion):
        thread_id = "thread_id"
        agent_id = "agent_id"
        body = {"agent_id": agent_id}

        agent.runs.create(thread_id, agent_id=agent_id)
        agent.runs.create(thread_id, body=body)
        agent.runs.create(thread_id, body=dict_to_io_bytes(body))

        await async_agent.runs.create(thread_id, agent_id=agent_id)
        await async_agent.runs.create(thread_id, body=body)
        await async_agent.runs.create(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)

    @pytest.mark.asyncio
    @pytest.mark.skip("Defect: during body as JSON and IO Bytes don't, backend not called with stream=True")
    @assert_same_http_requests
    async def test_create_stream(
        self, agent: AgentsClient, async_agent: AsyncAgentsClient, assertion: OverloadAssertion
    ):
        thread_id = "thread_id"
        agent_id = "agent_id"
        body = {"agent_id": agent_id}

        agent.runs.stream(thread_id, agent_id=agent_id)
        agent.runs.stream(thread_id, body=body)
        agent.runs.stream(thread_id, body=dict_to_io_bytes(body))

        await async_agent.runs.stream(thread_id, agent_id=agent_id)
        await async_agent.runs.stream(thread_id, body=body)
        await async_agent.runs.stream(thread_id, body=dict_to_io_bytes(body))

        assertion.same_http_requests_from(operation_count=6, api_per_operation_count=1)
