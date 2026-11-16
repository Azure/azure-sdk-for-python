# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Responses feature activation is independent of the Invocations switch."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import httpx
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import (
    TaskManagerNotInitialized,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
)
from azure.ai.agentserver.core.tasks._manager import get_task_manager
from azure.ai.agentserver.responses import ResponseEventStream, ResponsesAgentServerHost, ResponsesServerOptions


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("store,background", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("stream", [False, True])
def test_responses_activation_and_request_mode_matrix(
    monkeypatch: pytest.MonkeyPatch,
    switch: bool,
    resilient: bool,
    steerable: bool,
    store: bool,
    background: bool,
    stream: bool,
) -> None:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    set_resilient_tasks_enabled(switch)
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    assert resilient_tasks_enabled() is switch
    observed: list[tuple[bool, bool]] = []

    @host.response_handler
    async def handler(request, context, cancellation_signal):
        try:
            get_task_manager()
            manager_available = True
        except TaskManagerNotInitialized:
            manager_available = False
        observed.append((manager_available, context._task_context is not None))
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    with TestClient(host) as client:
        assert (host._task_manager is not None) is (resilient or steerable)
        response = client.post(
            "/responses",
            json={"model": "m", "input": "hello", "store": store, "background": background, "stream": stream},
        )
        if background and not store:
            assert response.status_code == 400
            assert response.json()["error"]["param"] == "background"
            assert observed == []
        else:
            assert response.status_code == 200, response.text
            assert observed == [((resilient or steerable), store and (resilient or steerable))]
    assert resilient_tasks_enabled() is switch


@pytest.mark.parametrize("resilient,steerable", [(False, True), (True, False), (True, True)])
@pytest.mark.asyncio
async def test_requested_runtime_startup_failure_is_not_downgraded(
    monkeypatch: pytest.MonkeyPatch, resilient: bool, steerable: bool
) -> None:
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    set_resilient_tasks_enabled(False)
    shutdown = AsyncMock()
    monkeypatch.setattr(TaskManager, "startup", AsyncMock(side_effect=RuntimeError("task store unavailable")))
    monkeypatch.setattr(TaskManager, "shutdown", shutdown)
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    with pytest.raises(RuntimeError, match="task store unavailable"):
        async with host.router.lifespan_context(host):
            pytest.fail("Startup must fail")
    assert host._task_manager is None
    shutdown.assert_awaited_once()


@pytest.mark.asyncio
async def test_overlapping_hosts_do_not_share_task_manager(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    providers = iter([LocalFileTaskProvider(tmp_path / "first"), LocalFileTaskProvider(tmp_path / "second")])
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(lambda _: next(providers)))
    set_resilient_tasks_enabled(False)
    first = ResponsesAgentServerHost(
        options=ResponsesServerOptions(steerable_conversations=True), configure_observability=None
    )
    second = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True), configure_observability=None
    )
    async with first.router.lifespan_context(first):
        first_manager = get_task_manager()
        async with second.router.lifespan_context(second):
            second_manager = get_task_manager()
            assert first_manager is not second_manager
        assert get_task_manager() is first_manager
        assert first._task_manager is first_manager
    assert first._task_manager is None
    assert second._task_manager is None


def test_disabled_responses_does_not_use_another_hosts_manager() -> None:
    set_resilient_tasks_enabled(True)
    enabled = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True), configure_observability=None
    )
    disabled = ResponsesAgentServerHost(configure_observability=None)
    observed: list[bool] = []

    @disabled.response_handler
    async def handler(request, context, cancellation_signal):
        with pytest.raises(TaskManagerNotInitialized):
            get_task_manager()
        observed.append(context._task_context is None)
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    with TestClient(enabled), TestClient(disabled) as client:
        result = client.post("/responses", json={"input": "hello", "store": True})
        assert result.status_code == 200, result.text
    assert observed == [True]


@pytest.mark.parametrize("multi_turn", [False, True])
@pytest.mark.parametrize("other_enabled", [False, True])
@pytest.mark.parametrize("construct_after_startup", [False, True])
@pytest.mark.parametrize("snapshot_mode", [False, True])
@pytest.mark.asyncio
async def test_recovery_uses_owning_hosts_handler_provider_and_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    multi_turn: bool,
    other_enabled: bool,
    construct_after_startup: bool,
    snapshot_mode: bool,
) -> None:
    from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager, _SCHEMA_VERSION, _SCHEMA_VERSION_KEY
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    from azure.ai.agentserver.responses import PlatformContext
    from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
    from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
    from azure.ai.agentserver.responses.models._generated import CreateResponse, ResponseObject
    from azure.ai.agentserver.responses.store._file import FileResponseStore

    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", "true" if snapshot_mode else "false")
    if snapshot_mode:
        monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "snapshot-owner-session")
        monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    task_store = LocalFileTaskProvider(tmp_path / "tasks")
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(lambda _: task_store))
    set_resilient_tasks_enabled(False)
    stores = [FileResponseStore(storage_dir=tmp_path / name) for name in ("first", "second")]
    first = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True, steerable_conversations=True),
        store=stores[0],
        configure_observability=None,
    )
    observed = []

    @first.response_handler
    async def first_handler(request, context, cancellation_signal):
        observed.append(("first", context.is_recovery, get_task_manager() is first._task_manager))
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        for event in events.output_item_message("recovered by first"):
            yield event
        yield events.emit_completed()

    def construct_other_host() -> ResponsesAgentServerHost:
        second = ResponsesAgentServerHost(
            options=ResponsesServerOptions(resilient_background=other_enabled),
            store=stores[1],
            configure_observability=None,
        )

        @second.response_handler
        async def second_handler(request, context, cancellation_signal):
            observed.append(("second", context.is_recovery, get_task_manager() is first._task_manager))
            events = ResponseEventStream(response_id=context.response_id, request=request)
            yield events.emit_created()
            for event in events.output_item_message("recovered by second"):
                yield event
            yield events.emit_completed()

        return second

    response_id = "resp_host_callback_owner"
    platform_context = PlatformContext(user_id_key="owner")
    for store in stores:
        await store.create_response(
            ResponseObject(
                {
                    "id": response_id,
                    "object": "response",
                    "status": "in_progress",
                    "background": True,
                    "model": "m",
                    "output": [],
                }
            ),
            [],
            None,
            context=platform_context,
        )
    orchestrator = first._endpoint._orchestrator._resilient_orchestrator
    primitive = orchestrator._multi_turn_task_fn if multi_turn else orchestrator._one_shot_task_fn

    async def persist_interrupted_task() -> None:
        request = CreateResponse(model="m", input="recover this", store=True, background=True, stream=False)
        if multi_turn:
            request["conversation"] = "conv_callback_owner"
        params = ResilientResponseInput(
            request=request, response_id=response_id, disposition="re-invoke", user_id_key="owner"
        ).to_task_input()
        payload = {"input": params, _SCHEMA_VERSION_KEY: _SCHEMA_VERSION}
        if multi_turn:
            payload["last_input_id"] = derive_lifecycle_id(response_id, "owner")
        agent = first.config.agent_name or "default"
        session = first.config.session_id or "local"
        info = await task_store.create(
            TaskCreateRequest(
                id=derive_lifecycle_id("task-owner", "owner"),
                agent_name=agent,
                session_id=session,
                status="in_progress",
                title="Interrupted response for callback ownership",
                payload=payload,
                tags={"task_name": primitive.name},
                source=TaskManager._build_source(primitive.name),
                lease_owner=derive_lease_owner(first.config.agent_name or "unknown-agent", session),
                lease_instance_id="interrupted-instance",
                lease_duration_seconds=60,
            )
        )
        assert info.lease is not None
        info.lease.expires_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        task_store._write_task(info)

    async def wait_for_terminal():
        while True:
            snapshots = [await store.get_response(response_id, context=platform_context) for store in stores]
            if any(snapshot["status"] in ("completed", "failed", "cancelled") for snapshot in snapshots):
                return snapshots
            await asyncio.sleep(0.01)

    if not construct_after_startup:
        construct_other_host()
        await persist_interrupted_task()
    async with first.router.lifespan_context(first):
        if snapshot_mode:
            assert first._task_manager is None
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=first), base_url="http://test") as client:
                restored = await client.post(
                    "/_agent/after-restore",
                    json={
                        "session_context": {
                            "session_id": "snapshot-owner-session",
                            "restore_id": "snapshot-owner-restore",
                            "session_env_overrides": {"FOUNDRY_AGENT_SESSION_GUID": "a" * 32},
                        }
                    },
                )
                assert restored.status_code == 200, restored.text
        if construct_after_startup:
            construct_other_host()
            await persist_interrupted_task()
            await first._task_manager._recover_stale_tasks()
        recovered, untouched = await asyncio.wait_for(wait_for_terminal(), timeout=10)
        assert observed == [("first", True, True)]
        assert recovered["status"] == "completed"
        assert recovered["output"][0]["content"][0]["text"] == "recovered by first"
        assert untouched["status"] == "in_progress"
        assert untouched["output"] == []
        assert first._task_manager._resume_callbacks[primitive.name] is primitive._fn
        assert first._task_manager._resume_opts[primitive.name] is primitive._opts
