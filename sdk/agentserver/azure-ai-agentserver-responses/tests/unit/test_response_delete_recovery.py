# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Crash-abandoned admission and durable, retryable scoped deletion regressions."""

from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest
from starlette.requests import Request

from azure.ai.agentserver.core.streaming import EventStreamNotFoundError
from azure.ai.agentserver.core.streaming._registry import _StreamsRegistry
from azure.ai.agentserver.core.tasks import TaskManagerNotInitialized
from azure.ai.agentserver.core.tasks._attachments import _resolve_input_storage
from azure.ai.agentserver.core.tasks._context import _ExitForRecovery
from azure.ai.agentserver.core.tasks._exceptions_internal import _HostedConflict
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, _SCHEMA_VERSION, _SCHEMA_VERSION_KEY
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskInfo, TaskPatchRequest
from azure.ai.agentserver.responses import PlatformContext, ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _response_task_lifecycle as lifecycle
from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
from azure.ai.agentserver.responses.models._generated import CreateResponse, ResponseObject
from azure.ai.agentserver.responses.models.runtime import ResponseExecution, ResponseModeFlags
from azure.ai.agentserver.responses.streaming import ResponseEventStream
from tests.contract.test_user_isolation_enforcement import _noop_handler
from tests.unit.test_stream_lifecycle_cleanup import RESPONSE_ID, _host, _request, registry


@pytest.fixture
def task_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LocalFileTaskProvider:
    provider = LocalFileTaskProvider(base_dir=tmp_path / "tasks")

    manager = TaskManager(_host().config, provider=provider)
    monkeypatch.setattr(lifecycle, "get_task_manager", lambda: manager)
    return provider


def _snapshot() -> ResponseObject:
    return ResponseObject(
        {"id": RESPONSE_ID, "object": "response", "status": "completed", "background": True, "model": "m", "output": []}
    )


def _delete_request() -> Request:
    request = _request()
    request.scope["method"] = "DELETE"
    request.scope["path_params"] = {"response_id": RESPONSE_ID}
    return request


def _execution(*, user: str = "owner", status: Any = "completed") -> ResponseExecution:
    return ResponseExecution(
        response_id=RESPONSE_ID,
        user_id_key=user,
        mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
        status=status,
        response=_snapshot() if status == "completed" else None,
    )


def _params(*, user: str = "owner", response_id: str = RESPONSE_ID, disposition: str = "re-invoke") -> dict[str, Any]:
    return ResilientResponseInput(
        request=CreateResponse(model="m", stream=True, store=True, background=True, input="hi"),
        response_id=response_id,
        disposition=disposition,
        user_id_key=user,
    ).to_task_input()


async def _durable_task(
    provider: LocalFileTaskProvider,
    host: ResponsesAgentServerHost,
    *,
    user: str = "owner",
    disposition: str = "re-invoke",
    multi_turn: bool = False,
    attached: bool = False,
    queued: bool = False,
) -> TaskInfo:
    task_id = derive_lifecycle_id(f"task-{RESPONSE_ID}", user)
    params = _params(user=user, disposition=disposition)
    payload: dict[str, Any] = {"input": params, _SCHEMA_VERSION_KEY: _SCHEMA_VERSION}
    attachments = None
    if attached:
        _, slot = _resolve_input_storage(params, threshold_bytes=0, key_for_attachment="input", task_id=task_id)
        payload["input"] = slot
        attachments = {"input": params}
    if multi_turn:
        payload["last_input_id"] = derive_lifecycle_id(RESPONSE_ID, user)
    if queued:
        payload["input"] = _params(user=user, response_id="another-response")
        payload["last_input_id"] = derive_lifecycle_id("another-response", user)
        _, slot = _resolve_input_storage(params, threshold_bytes=0, key_for_attachment="input", task_id=task_id)
        payload["steering"] = {"pending_inputs": [slot]}
        attachments = {"input": params}
    name = host._endpoint._response_task_names()[int(multi_turn)]
    return await provider.create(
        TaskCreateRequest(
            id=task_id,
            agent_name=host.config.agent_name or "default",
            session_id=host.config.session_id or "local",
            title="Response lifecycle regression",
            payload=payload,
            attachments=attachments,
            tags={"task_name": name},
            source=TaskManager._build_source(name),
        )
    )


def _task_context(info: TaskInfo, *, disposition: str = "re-invoke", entry_mode: str = "recovered") -> Any:
    return SimpleNamespace(
        task_id=info.id,
        input=_params(disposition=disposition),
        entry_mode=entry_mode,
        is_steered_turn=False,
        pending_input_count=0,
        cancel=asyncio.Event(),
        shutdown=asyncio.Event(),
    )


@pytest.mark.parametrize(
    "ownership",
    ["orphan", "live", "pending", "provider", "durable", "queued", "foreign", "closed", "fenced", "terminal"],
)
async def test_empty_cold_file_replay_requires_proven_absence_of_ownership(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    tmp_path: Path,
    ownership: str,
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    provider = host._endpoint._provider
    storage = tmp_path / "streams"
    first = _StreamsRegistry()
    first.use_file_backed_replay(storage_dir=storage, cursor_fn=lambda event: event["sequence_number"])
    stream_id = derive_lifecycle_id(RESPONSE_ID, "owner")
    abandoned = await first.get_or_create(stream_id)
    if ownership == "closed":
        await abandoned.close()
    abandoned._cleanup_locks()  # Simulate process loss without closing an ACTIVE log.
    registry.use_file_backed_replay(storage_dir=storage, cursor_fn=lambda event: event["sequence_number"])
    if ownership == "live":
        await state.add(_execution(status="in_progress"))
    elif ownership == "pending":
        assert await state.add_pending(_execution(status="in_progress"))
    elif ownership == "provider":
        await provider.create_response(_snapshot(), [], None, context=PlatformContext(user_id_key="owner"))
    elif ownership in {"durable", "queued"}:
        await _durable_task(task_store, host, attached=True, queued=ownership == "queued")
    elif ownership in {"fenced", "terminal"}:
        info = await _durable_task(task_store, host)
        if ownership == "fenced":
            await lifecycle._fence_response_tasks(RESPONSE_ID, "owner", host._endpoint._response_task_names())
        else:
            await task_store.update(info.id, TaskPatchRequest(status="completed"))
    other_id = derive_lifecycle_id(RESPONSE_ID, "other")
    other = await registry.get_or_create(other_id)
    await other.emit({"sequence_number": 0, "type": "response.created"})
    other_record = _execution(user="other", status="in_progress")
    await state.add(other_record)
    await provider.create_response(_snapshot(), [], None, context=PlatformContext(user_id_key="other"))
    foreign = await _durable_task(task_store, host, user="other")
    before = abandoned._path.read_bytes()
    try:
        available = await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        assert available is (ownership in {"orphan", "foreign", "fenced", "terminal"})
        if available:
            with pytest.raises(EventStreamNotFoundError):
                await registry.get(stream_id)
            assert not abandoned._path.exists()
            assert not await state.reserve(RESPONSE_ID, "owner")
            await state.release_reservation(RESPONSE_ID, "owner")
            assert await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
            await state.release_reservation(RESPONSE_ID, "owner")
        else:
            assert abandoned._path.read_bytes() == before
        assert await state.get(RESPONSE_ID, "other") is other_record
        assert await registry.get(other_id) is other
        assert (await task_store.get(foreign.id)).payload == foreign.payload
        assert (await provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="other")))[
            "id"
        ] == RESPONSE_ID
    finally:
        await registry.delete(stream_id)
        await registry.delete(other_id)


async def test_nonempty_cursorless_file_is_not_mistaken_for_an_empty_orphan(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, tmp_path: Path
) -> None:
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams")
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    replay = await registry.get_or_create(identifier)
    await replay.emit({"private": "retained"})
    assert await replay.last_cursor() is None
    try:
        assert not await _host()._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        assert await registry.get(identifier) is replay
    finally:
        await registry.delete(identifier)


async def test_failed_orphan_file_cleanup_can_be_retried_without_admitting_a_tombstoned_stream(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    replay = await registry.get_or_create(identifier)
    unlink = Path.unlink

    def denied(path: Path, *args: Any, **kwargs: Any) -> None:
        if path == replay._path:
            raise PermissionError("orphan file removal denied")
        unlink(path, *args, **kwargs)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            with pytest.raises(PermissionError):
                await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        with pytest.raises(EventStreamNotFoundError):
            await replay.last_cursor()
        assert await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        assert not replay._path.exists()
        with pytest.raises(EventStreamNotFoundError):
            await registry.get(identifier)
        await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")
    finally:
        await registry.delete(identifier)


async def test_missing_provider_recovery_does_not_leave_a_phantom_runtime_owner(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider
) -> None:
    host = _host()
    info = await _durable_task(task_store, host)
    await host._endpoint._orchestrator._resilient_orchestrator._execute_in_task(_task_context(info))
    assert await host._endpoint._runtime_state.list_records() == []
    assert await host._endpoint._runtime_state.reserve(RESPONSE_ID, "owner")
    await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")


async def test_orphan_reclamation_requires_available_durable_ownership_lookup(
    registry: _StreamsRegistry, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    replay = await registry.get_or_create(identifier)

    def unavailable() -> Any:
        raise TaskManagerNotInitialized("durable ownership unavailable")

    monkeypatch.setattr(lifecycle, "get_task_manager", unavailable)
    try:
        with pytest.raises(TaskManagerNotInitialized):
            await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        assert await registry.get(identifier) is replay
        assert replay._path.read_bytes() == b""
        assert await host._endpoint._runtime_state.reserve(RESPONSE_ID, "owner")
        await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")
    finally:
        await registry.delete(identifier)


async def test_orphan_probe_forwards_current_platform_call_identity(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    await registry.get_or_create(identifier)

    async def missing(response_id: str, *, context: PlatformContext) -> Any:
        assert response_id == RESPONSE_ID
        assert context.user_id_key == "owner"
        assert context.call_id == "current-call"
        raise KeyError(response_id)

    monkeypatch.setattr(host._endpoint._provider, "get_response", missing)
    request = _request()
    request.scope["headers"].append((b"x-agent-foundry-call-id", b"current-call"))
    response = await host._endpoint.handle_create(request)
    assert response.status_code == 200

    async def failed_headers(message: dict[str, Any]) -> None:
        raise OSError("headers failed")

    with pytest.raises(OSError, match="headers failed"):
        await response.stream_response(failed_headers)
    assert await host._endpoint._runtime_state.reserve(RESPONSE_ID, "owner")
    await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")


async def test_crash_empty_replay_is_replaced_by_successful_same_user_execution(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, tmp_path: Path
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    await registry.get_or_create(identifier)

    async def successful(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
        async def events() -> Any:
            stream = ResponseEventStream(response_id=context.response_id, model="m")
            yield stream.emit_created()
            yield stream.emit_completed()

        return events()

    host.response_handler(successful)
    response = await host._endpoint.handle_create(_request())
    assert response.status_code == 200
    sent = []

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    try:
        await asyncio.wait_for(response.stream_response(send), 2)
        body = b"".join(message.get("body", b"") for message in sent)
        assert b"response.created" in body
        assert b"response.completed" in body
        assert (await host._endpoint._provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner")))[
            "status"
        ] == "completed"
        assert (await host._endpoint.handle_create(_request())).status_code == 409
    finally:
        await registry.delete(identifier)


@pytest.mark.parametrize("failure", ["provider", "tasks", "cleanup"])
async def test_orphan_probe_failure_is_fail_closed_and_releases_only_its_reservation(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failure: str,
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    replay = await registry.get_or_create(identifier)
    delete = registry.delete
    fail = AsyncMock(side_effect=OSError("ownership or cleanup unavailable"))
    if failure == "provider":
        monkeypatch.setattr(host._endpoint._provider, "get_response", fail)
    elif failure == "tasks":
        monkeypatch.setattr(
            lifecycle, "get_task_manager", lambda: SimpleNamespace(provider=task_store, list_tasks=fail)
        )
    else:
        monkeypatch.setattr(registry, "delete", fail)
    try:
        with pytest.raises(OSError, match="ownership or cleanup unavailable"):
            await host._endpoint.handle_create(_request())
        assert await registry.get(identifier) is replay
        assert await host._endpoint._runtime_state.reserve(RESPONSE_ID, "owner")
        await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")
    finally:
        await delete(identifier)


async def test_orphan_reclamation_holds_scoped_admission_until_file_cleanup_finishes(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    host = _host()
    registry.use_file_backed_replay(storage_dir=tmp_path / "streams", cursor_fn=lambda event: event["sequence_number"])
    identifier = derive_lifecycle_id(RESPONSE_ID, "owner")
    await registry.get_or_create(identifier)
    reached = asyncio.Event()
    release = asyncio.Event()
    original = registry.delete

    async def paused_delete(key: str) -> None:
        reached.set()
        await release.wait()
        await original(key)

    monkeypatch.setattr(registry, "delete", paused_delete)
    claiming = asyncio.create_task(host._endpoint._reserve_response_id(RESPONSE_ID, "owner"))
    try:
        await asyncio.wait_for(reached.wait(), 2)
        assert not await host._endpoint._reserve_response_id(RESPONSE_ID, "owner")
        assert not await host._endpoint._runtime_state.begin_deletion(RESPONSE_ID, "owner")
        assert await host._endpoint._runtime_state.reserve(RESPONSE_ID, "other")
    finally:
        release.set()
        assert await claiming
        await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "owner")
        await host._endpoint._runtime_state.release_reservation(RESPONSE_ID, "other")


@pytest.mark.parametrize("runtime_record", [False, True])
@pytest.mark.parametrize("failure", ["error", "cancel", "cancel_after_write"])
@pytest.mark.parametrize("restart", [False, True])
async def test_provider_delete_failure_and_cancellation_retain_retryable_ownership(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    monkeypatch: pytest.MonkeyPatch,
    runtime_record: bool,
    failure: str,
    restart: bool,
) -> None:
    host = _host()
    provider = host._endpoint._provider
    state = host._endpoint._runtime_state
    await provider.create_response(_snapshot(), [], None, context=PlatformContext(user_id_key="owner"))
    record = _execution()
    if runtime_record:
        await state.add(record)
    other = _execution(user="other")
    await state.add(other)
    replay = await registry.get_or_create(derive_lifecycle_id(RESPONSE_ID, "owner"))
    await replay.emit({"sequence_number": 0, "type": "response.completed"})
    await replay.close()
    info = await _durable_task(task_store, host)
    delete = provider.delete_response

    async def fail_delete(*args: Any, **kwargs: Any) -> None:
        if failure == "error":
            raise OSError("provider deletion unavailable")
        if failure == "cancel_after_write":
            await delete(*args, **kwargs)
        raise asyncio.CancelledError()

    monkeypatch.setattr(provider, "delete_response", fail_delete)
    if failure == "error":
        failed = await host._endpoint.handle_delete(_delete_request())
        assert failed.status_code == 500
    else:
        with pytest.raises(asyncio.CancelledError):
            await host._endpoint.handle_delete(_delete_request())
    retained = await state.get(RESPONSE_ID, "owner")
    assert retained is not None
    if runtime_record:
        assert retained is record
    assert not await state.is_deleted(RESPONSE_ID, "owner")
    assert not await state.try_evict(RESPONSE_ID, "owner")
    assert not await state.reserve(RESPONSE_ID, "owner")
    assert await state.get(RESPONSE_ID, "other") is other
    assert await lifecycle._task_input_deleted(info.id, RESPONSE_ID, "owner")
    monkeypatch.setattr(provider, "delete_response", delete)
    if restart:
        restarted = ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=False), store=provider)
        restarted.response_handler(_noop_handler)
        host = restarted
    retried = await host._endpoint.handle_delete(_delete_request())
    assert retried.status_code == (404 if restart and failure == "cancel_after_write" else 200)
    with pytest.raises(KeyError):
        await provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))
    assert await host._endpoint._runtime_state.get(RESPONSE_ID, "owner") is None
    admitted = AsyncMock()
    monkeypatch.setattr(host._endpoint._orchestrator._resilient_orchestrator, "_execute_admitted_task", admitted)
    await host._endpoint._orchestrator._resilient_orchestrator._execute_in_task(_task_context(info))
    admitted.assert_not_awaited()
    assert (await host._endpoint.handle_delete(_delete_request())).status_code == 404


@pytest.mark.parametrize("disposition", ["re-invoke", "mark-failed"])
@pytest.mark.parametrize("runtime_record", [False, True])
async def test_recovery_defers_during_delete_and_cannot_resurrect_after_delete_or_restart(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    monkeypatch: pytest.MonkeyPatch,
    disposition: str,
    runtime_record: bool,
) -> None:
    host = _host()
    provider = host._endpoint._provider
    await provider.create_response(_snapshot(), [], None, context=PlatformContext(user_id_key="owner"))
    if runtime_record:
        await host._endpoint._runtime_state.add(_execution())
    info = await _durable_task(task_store, host, disposition=disposition, multi_turn=True)
    ctx = _task_context(info, disposition=disposition)
    orchestrator = host._endpoint._orchestrator._resilient_orchestrator
    admitted = AsyncMock()
    monkeypatch.setattr(orchestrator, "_execute_admitted_task", admitted)
    reached = asyncio.Event()
    release = asyncio.Event()
    update = task_store.update

    async def pause_fence(*args: Any, **kwargs: Any) -> TaskInfo:
        reached.set()
        await release.wait()
        return await update(*args, **kwargs)

    monkeypatch.setattr(task_store, "update", pause_fence)
    deleting = asyncio.create_task(host._endpoint.handle_delete(_delete_request()))
    try:
        await asyncio.wait_for(reached.wait(), 2)
        assert isinstance(await orchestrator._execute_in_task(ctx), _ExitForRecovery)
        admitted.assert_not_awaited()
        assert (await host._endpoint.handle_create(_request())).status_code == 409
        release.set()
        assert (await deleting).status_code == 200
    finally:
        release.set()
        await asyncio.gather(deleting, return_exceptions=True)
    await orchestrator._execute_in_task(ctx)
    admitted.assert_not_awaited()
    assert await host._endpoint._runtime_state.get(RESPONSE_ID, "owner") is None
    assert await host._endpoint._runtime_state.is_deleted(RESPONSE_ID, "owner")
    # Core turn completion patches only its own payload fields. The response
    # fence must survive that transition and protect a new process.
    await task_store.update(info.id, TaskPatchRequest(payload={"input": None, "retry_attempt": None}))
    restarted = ResponsesAgentServerHost(options=ResponsesServerOptions(resilient_background=False), store=provider)
    restarted.response_handler(_noop_handler)
    recovered = restarted._endpoint._orchestrator._resilient_orchestrator
    monkeypatch.setattr(recovered, "_execute_admitted_task", admitted)
    await recovered._execute_in_task(ctx)
    ctx.input.pop("agent_reference")
    await recovered._execute_in_task(ctx)  # Malformed input must not synthesize a deleted failed response.
    admitted.assert_not_awaited()
    assert await restarted._endpoint._runtime_state.list_records() == []
    with pytest.raises(KeyError):
        await provider.get_response(RESPONSE_ID, context=PlatformContext(user_id_key="owner"))


async def test_durable_fence_cas_retry_preserves_other_turns_queues_and_users(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _host()
    info = await _durable_task(task_store, host, multi_turn=True)
    foreign = await _durable_task(task_store, host, user="other", multi_turn=True)
    names = host._endpoint._response_task_names()
    original = task_store.update
    attempts = 0
    next_input = _params(response_id="next-response")
    queued_input = _params(response_id="queued-response")

    async def conflict_once(task_id: str, patch: TaskPatchRequest) -> TaskInfo:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            await original(
                task_id,
                TaskPatchRequest(
                    payload={
                        "input": next_input,
                        "last_input_id": derive_lifecycle_id("next-response", "owner"),
                        "steering": {"pending_inputs": [queued_input]},
                    }
                ),
            )
            raise _HostedConflict(_code="etag_mismatch", status_code=412)
        return await original(task_id, patch)

    monkeypatch.setattr(task_store, "update", conflict_once)
    await lifecycle._fence_response_tasks(RESPONSE_ID, "owner", names)
    assert attempts == 2
    updated = await task_store.get(info.id)
    assert updated.payload["input"] == next_input
    assert updated.payload["steering"]["pending_inputs"] == [queued_input]
    assert updated.payload["last_input_id"] == derive_lifecycle_id("next-response", "owner")
    assert await lifecycle._task_input_deleted(info.id, RESPONSE_ID, "owner")
    assert not await lifecycle._task_input_deleted(info.id, "next-response", "owner")
    assert not await lifecycle._task_input_deleted(foreign.id, RESPONSE_ID, "other")
    assert (await task_store.get(foreign.id)).to_dict() == foreign.to_dict()


@pytest.mark.parametrize("entry_mode", ["fresh", "resumed", "queued", "recovered"])
async def test_deleted_durable_input_is_never_dispatched(
    registry: _StreamsRegistry, task_store: LocalFileTaskProvider, monkeypatch: pytest.MonkeyPatch, entry_mode: str
) -> None:
    host = _host()
    info = await _durable_task(task_store, host)
    await lifecycle._fence_response_tasks(RESPONSE_ID, "owner", host._endpoint._response_task_names())
    orchestrator = host._endpoint._orchestrator._resilient_orchestrator
    admitted = AsyncMock()
    monkeypatch.setattr(orchestrator, "_execute_admitted_task", admitted)
    await orchestrator._execute_in_task(_task_context(info, entry_mode=entry_mode))
    admitted.assert_not_awaited()


@pytest.mark.parametrize("stale_record", [False, True])
async def test_normal_recovery_owns_reservation_through_handler_and_releases_it_on_failure(
    registry: _StreamsRegistry,
    task_store: LocalFileTaskProvider,
    monkeypatch: pytest.MonkeyPatch,
    stale_record: bool,
) -> None:
    host = _host()
    state = host._endpoint._runtime_state
    info = await _durable_task(task_store, host)
    if stale_record:
        record = _execution(status="in_progress")
        record.execution_task = asyncio.create_task(asyncio.sleep(0))
        await record.execution_task
        await state.add(record)
    orchestrator = host._endpoint._orchestrator._resilient_orchestrator

    async def execute(ctx: Any) -> None:
        assert not await state.reserve(RESPONSE_ID, "owner")
        if not stale_record:
            assert not await state.begin_deletion(RESPONSE_ID, "owner")
        assert await state.reserve(RESPONSE_ID, "other")
        await state.release_reservation(RESPONSE_ID, "other")
        raise RuntimeError("recoverable handler failure")

    monkeypatch.setattr(orchestrator, "_execute_admitted_task", execute)
    with pytest.raises(RuntimeError, match="recoverable handler failure"):
        await orchestrator._execute_in_task(_task_context(info))
    assert await state.reserve(RESPONSE_ID, "owner", recovery=True)
    await state.release_reservation(RESPONSE_ID, "owner")


async def test_runtime_completed_deletion_fences_recovery_but_allows_explicit_fresh_reuse() -> None:
    state = _RuntimeState()
    await state.mark_deleted(RESPONSE_ID, "owner")
    assert not await state.reserve(RESPONSE_ID, "owner", recovery=True)
    assert await state.reserve(RESPONSE_ID, "other", recovery=True)
    await state.release_reservation(RESPONSE_ID, "other")
    assert await state.reserve(RESPONSE_ID, "owner")
    assert not await state.reserve(RESPONSE_ID, "owner", recovery=True)
    await state.release_reservation(RESPONSE_ID, "owner")
