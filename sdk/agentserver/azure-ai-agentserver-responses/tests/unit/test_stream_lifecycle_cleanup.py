# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Admission, recovery, and pre-iteration cleanup of caller-scoped streams."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from starlette.requests import Request

from azure.ai.agentserver.core.streaming import EventStreamNotFoundError
from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry
from azure.ai.agentserver.core.tasks import LastInputIdPreconditionFailed, TaskConflictError
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses import PlatformContext
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.hosting import _endpoint_handler as endpoint
from azure.ai.agentserver.responses.hosting import _orchestrator as orchestration
from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as resilience
from azure.ai.agentserver.responses.hosting import _routing as routing
from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
from azure.ai.agentserver.responses.models._generated import CreateResponse, ResponseObject
from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags
from tests.contract.test_user_isolation_enforcement import _PartitionedProvider


RESPONSE_ID = IdGenerator.new_response_id()


@pytest.fixture
def registry(monkeypatch: pytest.MonkeyPatch) -> _StreamsRegistry:
    value = _StreamsRegistry()
    value.use_in_memory_replay(cursor_fn=lambda event: event["sequence_number"])
    for module in (endpoint, orchestration, resilience):
        monkeypatch.setattr(module, "streams", value)
    monkeypatch.setattr(routing, "_configure_streams_registry", lambda options: None)
    monkeypatch.setattr(endpoint, "_flush_spans_for_mode", AsyncMock())
    monkeypatch.setattr(resilience, "_RUNTIME_REFS", {})
    return value


def _request(*, user: str = "owner", background: bool = True) -> Request:
    body = json.dumps(
        {
            "response_id": RESPONSE_ID,
            "model": "m",
            "input": "hi",
            "store": True,
            "stream": True,
            "background": background,
        }
    ).encode()
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "method": "POST",
        "path": "/responses",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json"), (b"x-agent-user-id", user.encode())],
    }
    return Request(scope, AsyncMock(return_value={"type": "http.request", "body": body, "more_body": False}))


def _host() -> ResponsesAgentServerHost:
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=False), store=_PartitionedProvider()
    )

    async def handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        raise AssertionError("rejected admission must not invoke the handler")
        yield

    host.response_handler(handler)
    return host


async def _send(message: dict[str, Any]) -> None:
    pass


@pytest.mark.parametrize("failure", ["conflict", "precondition", "cancel"])
async def test_rejected_admission_deletes_new_stream_before_releasing_reservation(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    other_id = derive_lifecycle_id(RESPONSE_ID, "other")
    other = await registry.get_or_create(other_id)
    cleanup_started = asyncio.Event()
    finish_cleanup = asyncio.Event()
    original_delete = registry.delete

    async def delete(stream_id: str) -> None:
        assert stream_id == lifecycle_id
        cleanup_started.set()
        await finish_cleanup.wait()
        await original_delete(stream_id)

    async def reject(*args: Any, **kwargs: Any) -> bool:
        if failure == "cancel":
            raise asyncio.CancelledError()
        if failure == "precondition":
            raise LastInputIdPreconditionFailed(actual_last_input_id="latest")
        raise TaskConflictError(current_status="in_progress")

    monkeypatch.setattr(registry, "delete", delete)
    monkeypatch.setattr(resilience.ResilientResponseOrchestrator, "start_resilient", reject)
    response = await host._endpoint.handle_create(_request())
    sending = asyncio.create_task(response.stream_response(_send))
    try:
        await asyncio.wait_for(cleanup_started.wait(), 2)
        assert await state.list_records() == []
        competing = await host._endpoint.handle_create(_request())
        assert competing.status_code == 409
        assert json.loads(competing.body)["error"]["code"] == "response_id_conflict"
    finally:
        finish_cleanup.set()
    expected = {
        "conflict": TaskConflictError,
        "precondition": LastInputIdPreconditionFailed,
        "cancel": asyncio.CancelledError,
    }[failure]
    with pytest.raises(expected):
        await asyncio.wait_for(sending, 2)
    with pytest.raises(EventStreamNotFoundError):
        await registry.get(lifecycle_id)
    assert await registry.get(other_id) is other
    assert await state.reserve(RESPONSE_ID, "owner")
    await state.release_reservation(RESPONSE_ID, "owner")
    retry = await host._endpoint.handle_create(_request())
    assert retry.status_code == 200

    # Headers fail before lazy task admission, so this second create allocates no stream.
    async def fail_headers(message: dict[str, Any]) -> None:
        raise OSError("headers failed")

    with pytest.raises(OSError):
        await retry.stream_response(fail_headers)
    assert await state.reserve(RESPONSE_ID, "owner")
    await state.release_reservation(RESPONSE_ID, "owner")


async def test_rejected_admission_preserves_preexisting_stream(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _host()
    response = await host._endpoint.handle_create(_request())
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    existing = await registry.get_or_create(lifecycle_id)
    await existing.emit({"sequence_number": 0, "type": "response.created"})
    monkeypatch.setattr(
        resilience.ResilientResponseOrchestrator,
        "start_resilient",
        AsyncMock(side_effect=TaskConflictError(current_status="in_progress")),
    )
    with pytest.raises(TaskConflictError):
        await response.stream_response(_send)
    assert await registry.get(lifecycle_id) is existing
    await existing.close()
    assert [event async for event in existing.subscribe()] == [{"sequence_number": 0, "type": "response.created"}]


@pytest.mark.parametrize("file_backed", [False, True])
@pytest.mark.parametrize("send_error", [False, True])
async def test_shutdown_rejection_deletes_new_replay_before_yield_and_reservation_release(
    registry: _StreamsRegistry,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    file_backed: bool,
    send_error: bool,
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    other_id = derive_lifecycle_id(RESPONSE_ID, "other")
    storage_dir = tmp_path / "replay"
    if file_backed:
        registry.use_file_backed_replay(storage_dir=storage_dir, cursor_fn=lambda event: event["sequence_number"])
    other = await registry.get_or_create(other_id)
    started = AsyncMock()
    monkeypatch.setattr(resilience.ResilientResponseOrchestrator, "start_resilient", started)
    response = await host._endpoint.handle_create(_request())
    await state.begin_draining()
    deleting = asyncio.Event()
    release_delete = asyncio.Event()
    original_delete = registry.delete
    frames: list[bytes] = []

    async def delete(stream_id: str) -> None:
        assert stream_id == lifecycle_id
        deleting.set()
        await release_delete.wait()
        await original_delete(stream_id)

    async def send(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.body" and message.get("body"):
            with pytest.raises(EventStreamNotFoundError):
                await registry.get(lifecycle_id)
            frames.append(message["body"])
            if send_error:
                raise OSError("client disconnected")

    monkeypatch.setattr(registry, "delete", delete)
    sending = asyncio.create_task(response.stream_response(send))
    try:
        await asyncio.wait_for(deleting.wait(), 2)
        assert not frames
        assert not await state.reserve(RESPONSE_ID, "owner")
        competing = await host._endpoint.handle_create(_request())
        assert competing.status_code == 409
        assert json.loads(competing.body)["error"]["code"] == "response_id_conflict"
        assert await state.list_records() == []
    finally:
        release_delete.set()
    if send_error:
        with pytest.raises(OSError, match="client disconnected"):
            await asyncio.wait_for(sending, 2)
    else:
        await asyncio.wait_for(sending, 2)
    started.assert_not_awaited()
    error = json.loads(frames[0].decode().split("data: ", 1)[1].strip())
    assert error["type"] == "error"
    assert error["code"] == "server_error"
    with pytest.raises(EventStreamNotFoundError):
        await registry.get(lifecycle_id)
    assert await registry.get(other_id) is other
    assert await state.reserve(RESPONSE_ID, "owner")
    await state.release_reservation(RESPONSE_ID, "owner")
    with pytest.raises(KeyError):
        await host._endpoint._provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))
    if file_backed:
        # Only the other user's log remains; failed admission left no cleanup owner.
        assert len(list(storage_dir.glob("*.jsonl"))) == 1
        await original_delete(other_id)


@pytest.mark.parametrize("existing_stream", [False, True])
async def test_shutdown_rejection_preserves_existing_stream_and_started_record(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, existing_stream: bool
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    response = await host._endpoint.handle_create(_request())
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    active = await registry.get_or_create(lifecycle_id) if existing_stream else None
    if active is not None:
        await active.emit({"type": "response.created", "sequence_number": 0})
    record = ResponseExecution(
        response_id=RESPONSE_ID,
        user_id_key="owner",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
        status="in_progress",
        subject=active,
    )
    running = asyncio.create_task(asyncio.Event().wait())
    record.execution_task = running
    await state.add(record)
    await state.begin_draining()
    started = AsyncMock()
    monkeypatch.setattr(resilience.ResilientResponseOrchestrator, "start_resilient", started)
    delete = AsyncMock(wraps=registry.delete)
    monkeypatch.setattr(registry, "delete", delete)
    try:
        await asyncio.wait_for(response.stream_response(_send), 2)
        started.assert_not_awaited()
        delete.assert_not_awaited()
        assert await state.get(RESPONSE_ID, "owner") is record
        assert not running.done()
        retained = await registry.get(lifecycle_id)
        if active is not None:
            assert retained is active
        else:
            active = retained
            await active.emit({"type": "response.created", "sequence_number": 0})
        await active.emit({"type": "response.completed", "sequence_number": 1}, close=True)
        assert [event["type"] async for event in active.subscribe()] == ["response.created", "response.completed"]
    finally:
        running.cancel()
        await asyncio.gather(running, return_exceptions=True)


@pytest.mark.parametrize("background", [False, True])
@pytest.mark.parametrize("failure", ["error", "cancel"])
async def test_header_failure_stops_monitor_and_releases_exactly_once(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, background: bool, failure: str
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    monitors: list[asyncio.Task[Any]] = []

    async def monitor(request: Any, signal: asyncio.Event, **kwargs: Any) -> None:
        monitors.append(asyncio.current_task())
        await signal.wait()

    monkeypatch.setattr(host._endpoint, "_monitor_disconnect", monitor)
    release = AsyncMock(wraps=state.release_reservation)
    monkeypatch.setattr(state, "release_reservation", release)
    response = await host._endpoint.handle_create(_request(background=background))

    async def fail_headers(message: dict[str, Any]) -> None:
        assert message["type"] == "http.response.start"
        if failure == "cancel":
            raise asyncio.CancelledError()
        raise OSError("headers failed")

    with pytest.raises(asyncio.CancelledError if failure == "cancel" else OSError):
        await response.stream_response(fail_headers)
    assert release.await_count == 1
    assert all(task.done() for task in monitors)
    assert len(monitors) == (0 if background else 1)
    assert await state.reserve(RESPONSE_ID, "owner")
    # Re-entering finalization must not release a later caller's reservation.
    with pytest.raises(asyncio.CancelledError if failure == "cancel" else OSError):
        await response.stream_response(fail_headers)
    assert release.await_count == 1
    assert not await state.reserve(RESPONSE_ID, "owner")
    await state.release_reservation(RESPONSE_ID, "owner")
    with pytest.raises(EventStreamNotFoundError):
        await registry.get(derive_lifecycle_id(RESPONSE_ID, "owner"))


@pytest.mark.parametrize("cancel_admission", [False, True])
async def test_started_background_execution_survives_failed_http_request(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, cancel_admission: bool
) -> None:
    host = _host()
    complete = asyncio.Event()
    execution: asyncio.Task[Any] | None = None
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")

    async def start(*args: Any, record: Any, **kwargs: Any) -> bool:
        nonlocal execution

        async def run() -> None:
            await record.subject.emit({"type": "response.created", "sequence_number": 0})
            await complete.wait()
            await record.subject.emit({"type": "response.completed", "sequence_number": 1}, close=True)

        execution = asyncio.create_task(run())
        record.execution_task = execution
        record.resilient_task_run = SimpleNamespace(is_queued=False)
        if cancel_admission:
            raise asyncio.CancelledError()
        return True

    monkeypatch.setattr(resilience.ResilientResponseOrchestrator, "start_resilient", start)
    response = await host._endpoint.handle_create(_request())

    async def fail_body(message: dict[str, Any]) -> None:
        if message["type"] == "http.response.body":
            raise OSError("body failed")

    try:
        with pytest.raises(asyncio.CancelledError if cancel_admission else OSError):
            await asyncio.wait_for(response.stream_response(fail_body), 2)
        assert execution is not None and not execution.done()
        retained = await registry.get(lifecycle_id)
    finally:
        complete.set()
        if execution is not None:
            await asyncio.wait_for(execution, 2)
    assert [event["type"] async for event in retained.subscribe()] == ["response.created", "response.completed"]
    competing = await host._endpoint.handle_create(_request())
    assert competing.status_code == 409


@pytest.mark.parametrize("terminal", [None, "completed", "failed"])
async def test_cold_mark_failed_recovery_finishes_replay_and_ttl(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, terminal: str | None
) -> None:
    host = _host()
    provider = host._endpoint._provider
    original = _StreamsRegistry()
    original.use_file_backed_replay(
        storage_dir=tmp_path, cursor_fn=lambda event: event["sequence_number"], ttl_seconds=10
    )
    response_id = RESPONSE_ID
    lifecycle_id = derive_lifecycle_id(response_id, "owner")
    other_id = derive_lifecycle_id(response_id, "other")
    snapshot = ResponseObject(
        {
            "id": response_id,
            "status": terminal or "in_progress",
            "object": "response",
            "background": True,
            "output": [],
            "agent_reference": {"type": "agent_reference", "name": "agent", "version": "1"},
        }
    )
    await provider.create_response(snapshot, [], None, context=PlatformContext(user_id_key="owner"))
    unfinished = await original.get_or_create(lifecycle_id)
    await unfinished.emit({"type": "response.created", "sequence_number": 4, "response": {"id": response_id}})
    unfinished._cleanup_locks()
    other = await original.get_or_create(other_id)
    await other.emit({"type": "response.created", "sequence_number": 0})
    other._cleanup_locks()
    registry.use_file_backed_replay(
        storage_dir=tmp_path, cursor_fn=lambda event: event["sequence_number"], ttl_seconds=10
    )
    orch = resilience.ResilientResponseOrchestrator(
        create_fn=AsyncMock(), provider=provider, options=ResponsesServerOptions()
    )
    params = ResilientResponseInput(
        request=CreateResponse({"input": "hi", "background": True, "store": True, "stream": True}),
        response_id=response_id,
        disposition="mark-failed",
        user_id_key="owner",
    ).to_task_input()
    try:
        assert await orch._handle_recovery_disposition(
            disposition="mark-failed", is_recovery=True, response_id=response_id, params=params, background=True
        )
        recovered = await registry.get(lifecycle_id)

        async def collect() -> list[dict[str, Any]]:
            return [event async for event in recovered.subscribe()]

        events = await asyncio.wait_for(collect(), 2)
        assert events[-1]["type"] == f"response.{terminal or 'failed'}"
        assert events[-1]["sequence_number"] == 5
        persisted = await provider.get_response(response_id, context=PlatformContext(user_id_key="owner"))
        assert persisted["status"] == (terminal or "failed")
        await orch._persist_crash_failed(response_id, params)
        assert len(await asyncio.wait_for(collect(), 2)) == 2
        request = _request()
        request.scope.update(
            method="GET",
            path=f"/responses/{response_id}",
            query_string=b"stream=true",
            path_params={"response_id": response_id},
        )
        replay = await host._endpoint.handle_get(request)
        assert replay.status_code == 200
        frames: list[bytes] = []

        async def send_replay(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.body":
                frames.append(message.get("body", b""))

        await asyncio.wait_for(replay.stream_response(send_replay), 2)
        assert f"response.{terminal or 'failed'}".encode() in b"".join(frames)
        other_replay = await registry.get(other_id)
        await other_replay.emit({"type": "response.in_progress", "sequence_number": 1})
        # Advancing the clock, rather than sleeping, verifies close-clock expiry.
        from azure.ai.agentserver.core.streaming import _concrete

        monkeypatch.setattr(_concrete.time, "time", lambda: recovered._close_time + 11)
        with pytest.raises(EventStreamNotFoundError):
            await registry.get(lifecycle_id)
        assert len(list(tmp_path.glob("*.jsonl"))) == 1
    finally:
        await registry.delete(lifecycle_id)
        await registry.delete(other_id)


async def test_resumable_recovery_keeps_active_replay(registry: _StreamsRegistry) -> None:
    host = _host()
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    active = await registry.get_or_create(lifecycle_id)
    orch = resilience.ResilientResponseOrchestrator(
        create_fn=AsyncMock(), provider=host._endpoint._provider, options=ResponsesServerOptions()
    )
    assert not await orch._handle_recovery_disposition(
        disposition="re-invoke", is_recovery=True, response_id=RESPONSE_ID, params={}, background=True
    )
    assert await registry.get(lifecycle_id) is active
    await active.emit({"type": "response.completed", "sequence_number": 1}, close=True)
    assert [event["type"] async for event in active.subscribe()] == ["response.completed"]


@pytest.mark.parametrize("failure", ["read", "write"])
async def test_uncertain_terminal_persistence_keeps_replay_active(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    host = _host()
    lifecycle_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    active = await registry.get_or_create(lifecycle_id)
    provider = host._endpoint._provider
    await provider.create_response(
        {"id": RESPONSE_ID, "status": "in_progress", "output": []},
        [],
        None,
        context=PlatformContext(user_id_key="owner"),
    )
    if failure == "read":
        monkeypatch.setattr(provider, "get_response", AsyncMock(side_effect=RuntimeError("store unavailable")))
    else:
        monkeypatch.setattr(provider, "update_response", AsyncMock(side_effect=RuntimeError("write rejected")))
    orch = resilience.ResilientResponseOrchestrator(
        create_fn=AsyncMock(), provider=provider, options=ResponsesServerOptions()
    )
    await orch._persist_crash_failed(RESPONSE_ID, {"user_id_key": "owner"})
    await active.emit({"type": "response.in_progress", "sequence_number": 0})
    assert await registry.get(lifecycle_id) is active
    await active.close()
    assert [event["type"] async for event in active.subscribe()] == ["response.in_progress"]


async def test_terminal_replay_cleanup_error_does_not_overwrite_completed_storage(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _host()
    provider = host._endpoint._provider
    await provider.create_response(
        {"id": RESPONSE_ID, "status": "completed", "output": []},
        [],
        None,
        context=PlatformContext(user_id_key="owner"),
    )
    await registry.get_or_create(derive_lifecycle_id(RESPONSE_ID, "owner"))
    monkeypatch.setattr(registry, "get", AsyncMock(side_effect=OSError("replay unavailable")))
    update = AsyncMock(wraps=provider.update_response)
    monkeypatch.setattr(provider, "update_response", update)
    orch = resilience.ResilientResponseOrchestrator(
        create_fn=AsyncMock(), provider=provider, options=ResponsesServerOptions()
    )
    with pytest.raises(OSError, match="replay unavailable"):
        await orch._persist_crash_failed(RESPONSE_ID, {"user_id_key": "owner"})
    update.assert_not_awaited()
    persisted = await provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))
    assert persisted["status"] == "completed"


async def test_mark_failed_recovery_never_allocates_an_absent_replay(
    registry: _StreamsRegistry, tmp_path: Path
) -> None:
    host = _host()
    storage_dir = tmp_path / "replay"
    registry.use_file_backed_replay(storage_dir=storage_dir, cursor_fn=lambda event: event["sequence_number"])
    orch = resilience.ResilientResponseOrchestrator(
        create_fn=AsyncMock(), provider=host._endpoint._provider, options=ResponsesServerOptions()
    )
    await orch._persist_crash_failed(RESPONSE_ID, {"user_id_key": "owner"})
    assert not list(storage_dir.iterdir())
    with pytest.raises(EventStreamNotFoundError):
        await registry.get(derive_lifecycle_id(RESPONSE_ID, "owner"))
