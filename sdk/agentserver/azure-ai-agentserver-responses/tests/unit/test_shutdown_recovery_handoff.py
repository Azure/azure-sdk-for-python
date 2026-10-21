# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Real task-context signal handoffs across durable response reconstruction."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks._context import TaskContext, _ExitForRecovery
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._models import TaskPatchRequest
from azure.ai.agentserver.responses import PlatformContext, ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as resilience
from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.streaming import ResponseEventStream
from tests.unit.test_response_delete_recovery import _durable_task, _params, _snapshot, task_store
from tests.unit.test_stream_lifecycle_cleanup import RESPONSE_ID, _request, registry


def _host(tmp_path: Path, handler: Any) -> ResponsesAgentServerHost:
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True, shutdown_grace_period_seconds=1),
        store=FileResponseStore(tmp_path / "responses"),
    )
    host.response_handler(handler)
    return host


async def _stored_context(
    host: ResponsesAgentServerHost, provider: LocalFileTaskProvider, *, stream: bool
) -> TaskContext[dict[str, Any]]:
    info = await _durable_task(provider, host)
    params = _params()
    params["request"]["stream"] = stream
    params["response_incarnation_id"] = "a" * 32
    await provider.update(info.id, TaskPatchRequest(payload={"input": params}))
    snapshot = _snapshot()
    snapshot["status"] = "in_progress"
    await host._endpoint._provider.create_response(snapshot, [], None, context=PlatformContext(user_id_key="owner"))
    return TaskContext(
        task_id=info.id,
        input_id=derive_lifecycle_id(RESPONSE_ID, "owner"),
        session_id="local",
        input=json.loads(json.dumps(params)),
        entry_mode="recovered",
    )


@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("explicit", [False, True])
async def test_response_shutdown_defers_real_task_before_manager_shutdown_and_recovers(
    registry, task_store, tmp_path, stream, explicit
):
    entered = asyncio.Event()
    contexts = []

    async def interrupted(request, context, cancellation_signal):
        contexts.append(context)
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_in_progress()
        yield events.checkpoint()
        entered.set()
        await cancellation_signal.wait()
        assert context.shutdown.is_set()
        if explicit:
            await context.exit_for_recovery()

    host = _host(tmp_path, interrupted)
    ctx = await _stored_context(host, task_store, stream=stream)
    executing = asyncio.create_task(host._endpoint._orchestrator._resilient_orchestrator._execute_in_task(ctx))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        record = await host._endpoint._runtime_state.get(RESPONSE_ID, "owner")
        assert record is not None
        assert record.execution_task is executing
        assert not ctx.shutdown.is_set()
        await asyncio.wait_for(host._endpoint.handle_shutdown(), 2)
        assert ctx.shutdown.is_set()
        assert isinstance(await executing, _ExitForRecovery)
        stored = await host._endpoint._provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))
        assert stored["status"] == "in_progress"
        assert host._endpoint._runtime_state._reservations == set()
        assert resilience._RUNTIME_REFS == {}

        seen = []

        async def resumed(request, context, cancellation_signal):
            seen.append((context.is_recovery, context.persisted_response["status"], context.shutdown.is_set()))
            events = ResponseEventStream(response_id=context.response_id, request=request)
            yield events.emit_created()
            yield events.emit_in_progress()
            yield events.emit_completed()

        restarted = _host(tmp_path, resumed)
        persisted_task = await task_store.get(ctx.task_id)
        assert persisted_task is not None
        recovered = TaskContext(
            task_id=ctx.task_id,
            input_id=ctx.input_id,
            session_id="local",
            input=json.loads(json.dumps(persisted_task.payload["input"])),
            entry_mode="recovered",
        )
        await restarted._endpoint._orchestrator._resilient_orchestrator._execute_in_task(recovered)
        assert seen == [(True, "in_progress", False)]
        terminal = await restarted._endpoint._provider.get_response(
            RESPONSE_ID, context=PlatformContext(user_id_key="owner")
        )
        assert terminal["status"] == "completed"
        assert restarted._endpoint._runtime_state._reservations == set()
        assert resilience._RUNTIME_REFS == {}
    finally:
        for context in contexts:
            context._cancellation_signal.set()
        if not executing.done():
            executing.cancel()
        await asyncio.gather(executing, return_exceptions=True)


@pytest.mark.parametrize("stream", [False, True])
async def test_cold_recovery_cancel_wakes_tracked_execution_and_persists_cancelled(
    registry, task_store, tmp_path, stream
):
    entered = asyncio.Event()
    signals = []
    contexts = []

    async def handler(request, context, cancellation_signal):
        signals.append(cancellation_signal)
        contexts.append(context)
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_in_progress()
        entered.set()
        await cancellation_signal.wait()
        assert context.client_cancelled
        assert not context.shutdown.is_set()

    host = _host(tmp_path, handler)
    ctx = await _stored_context(host, task_store, stream=stream)
    executing = asyncio.create_task(host._endpoint._orchestrator._resilient_orchestrator._execute_in_task(ctx))
    try:
        await asyncio.wait_for(entered.wait(), 2)
        record = await host._endpoint._runtime_state.get(RESPONSE_ID, "owner")
        assert record is not None
        assert record.execution_task is executing
        assert record.cancel_signal is signals[0]
        assert contexts[0]._cancellation_signal is signals[0]
        request = _request(stream=stream)
        request.scope["path_params"] = {"response_id": RESPONSE_ID}
        cancelled = await asyncio.wait_for(host._endpoint.handle_cancel(request), 2)
        assert cancelled.status_code == 200
        assert json.loads(cancelled.body)["status"] == "cancelled"
        await asyncio.wait_for(executing, 2)
        stored = await host._endpoint._provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))
        assert stored["status"] == "cancelled"
        assert not ctx.shutdown.is_set()
        assert host._endpoint._runtime_state._reservations == set()
        assert resilience._RUNTIME_REFS == {}
    finally:
        for signal in signals:
            signal.set()
        if not executing.done():
            executing.cancel()
        await asyncio.gather(executing, return_exceptions=True)


async def test_task_binding_preserves_shutdown_signalled_before_task_context_attachment(registry, tmp_path):
    async def handler(request, context, cancellation_signal):
        if False:
            yield

    host = _host(tmp_path, handler)
    record, context = resilience._reconstruct_from_params(
        params=_params(),
        response_id=RESPONSE_ID,
        provider=host._endpoint._provider,
        runtime_state=host._endpoint._runtime_state,
        runtime_options=host._endpoint._runtime_options,
    )
    context.shutdown.set()
    ctx = TaskContext(task_id="binding", session_id="local", input=_params())
    assert record.response_context is context
    assert not ctx.shutdown.is_set()
    assert not await host._endpoint._orchestrator._resilient_orchestrator._flatten_recovery_context(ctx, context, False)
    assert ctx.shutdown.is_set()


@pytest.mark.parametrize("stream", [False, True])
async def test_recovery_exit_outside_shutdown_keeps_core_misuse_guard(registry, task_store, tmp_path, stream):
    async def handler(request, context, cancellation_signal):
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_in_progress()
        await context.exit_for_recovery()

    host = _host(tmp_path, handler)
    ctx = await _stored_context(host, task_store, stream=stream)
    with pytest.raises(RuntimeError, match="ctx.exit_for_recovery.*ctx.shutdown.is_set"):
        await host._endpoint._orchestrator._resilient_orchestrator._execute_in_task(ctx)
    assert not ctx.shutdown.is_set()
    assert not await host._endpoint._runtime_state.is_draining()
    assert host._endpoint._runtime_state._reservations == set()
    assert resilience._RUNTIME_REFS == {}
