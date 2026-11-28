# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression coverage for native cached-task ownership (upstream issue #1159)."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    Artifact,
    CancelTaskRequest,
    Part,
    Role,
    SendMessageConfiguration,
    SendMessageRequest,
    SubscribeToTaskRequest,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils.errors import TaskNotFoundError

from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    get_request_context,
    reset_request_context,
    set_request_context,
)


class _HoldingExecutor(AgentExecutor):
    def __init__(self):
        self.release = asyncio.Event()
        self.finished = asyncio.Event()
        self.cancellations = 0

    async def execute(self, context, event_queue):
        try:
            await event_queue.enqueue_event(
                Task(
                    id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
                    artifacts=[Artifact(artifact_id="private", parts=[Part(text="private result")])],
                    history=[context.message],
                )
            )
            await self.release.wait()
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
                )
            )
        finally:
            self.finished.set()

    async def cancel(self, context, event_queue):
        self.cancellations += 1


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["subscribe", "cancel"])
@pytest.mark.parametrize("include_raw_user", [False, True])
async def test_another_caller_cannot_access_cached_active_task(monkeypatch, operation, include_raw_user):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "isolated-agent")
    monkeypatch.setenv("FOUNDRY_AGENT_ID", "isolated-agent-guid")
    records = {}
    backend = AsyncMock()
    backend.get.return_value = SimpleNamespace(user_isolation=True)
    callers = {"alice-call": "alice", "bob-call": "bob"}

    async def write(key, value, **kwargs):
        records[(callers[get_request_context().call_id], key)] = SimpleNamespace(key=key, value=value)

    async def read(key, **kwargs):
        return records.get((callers[get_request_context().call_id], key))

    backend.set_item.side_effect = write
    backend.get_item.side_effect = read
    factory = Mock(return_value=backend)
    factory.get_or_create = AsyncMock(return_value=backend)
    monkeypatch.setattr("azure.ai.agentserver.a2a._foundry_task_store.FoundryStateStore", factory)
    executor = _HoldingExecutor()
    host = A2AAgentServerHost(
        agent_card=AgentCard(name="isolated", version="1.0", capabilities=AgentCapabilities(streaming=True)),
        agent_executor=executor,
        configure_observability=None,
    )
    handler = host.request_handler
    context = ServerCallContext()
    alice = FoundryAgentRequestContext(user_id="alice" if include_raw_user else None, call_id="alice-call")
    token = set_request_context(alice)
    try:
        result = await asyncio.wait_for(
            handler.on_message_send(
                SendMessageRequest(
                    message=new_text_message("private input", role=Role.ROLE_USER),
                    configuration=SendMessageConfiguration(return_immediately=True),
                ),
                context,
            ),
            timeout=5,
        )
        assert isinstance(result, Task)
        task_id = result.id
    finally:
        reset_request_context(token)

    try:
        token = set_request_context(
            FoundryAgentRequestContext(user_id="bob" if include_raw_user else None, call_id="bob-call")
        )
        try:
            assert await host._owned_task_store.get(task_id, context) is None
            if operation == "subscribe":
                stream = handler.on_subscribe_to_task(SubscribeToTaskRequest(id=task_id), context)
                try:
                    with pytest.raises(TaskNotFoundError):
                        await asyncio.wait_for(anext(stream), timeout=5)
                finally:
                    await stream.aclose()
            else:
                with pytest.raises(TaskNotFoundError):
                    await asyncio.wait_for(handler.on_cancel_task(CancelTaskRequest(id=task_id), context), timeout=5)
                assert executor.cancellations == 0
        finally:
            reset_request_context(token)

        token = set_request_context(alice)
        try:
            stream = handler.on_subscribe_to_task(SubscribeToTaskRequest(id=task_id), context)
            try:
                owned = await asyncio.wait_for(anext(stream), timeout=5)
                assert owned.artifacts[0].parts[0].text == "private result"
                assert owned.history[0].parts[0].text == "private input"
            finally:
                await stream.aclose()
        finally:
            reset_request_context(token)
    finally:
        executor.release.set()
        await asyncio.wait_for(executor.finished.wait(), timeout=5)
        await host._dispatch_shutdown()
