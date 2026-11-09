# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Invocations enablement must remain independent of Responses features."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import (
    TaskContext,
    TaskManagerNotInitialized,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
    task,
)
from azure.ai.agentserver.core.tasks._manager import get_task_manager, set_task_manager
from azure.ai.agentserver.invocations import InvocationAgentServerHost


@pytest.fixture(autouse=True)
def isolated_tasks(monkeypatch: pytest.MonkeyPatch, tmp_path):
    from azure.ai.agentserver.core.tasks import _manager

    previous_flag = resilient_tasks_enabled()
    previous_manager = _manager._manager
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    set_resilient_tasks_enabled(False)
    set_task_manager(None)
    try:
        yield
    finally:
        set_resilient_tasks_enabled(previous_flag)
        set_task_manager(previous_manager)


def manager_available() -> bool:
    try:
        get_task_manager()
        return True
    except TaskManagerNotInitialized:
        return False


@pytest.mark.parametrize("path", ["/invocations_ws", "/voice_conversation_engine"])
@pytest.mark.parametrize("responses_first", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("enabled", [False, True])
def test_composed_voice_routes_mask_disabled_invocations_tasks(
    path: str, responses_first: bool, resilient: bool, steerable: bool, enabled: bool
) -> None:
    responses = pytest.importorskip("azure.ai.agentserver.responses")
    from azure.ai.agentserver.invocations.voice import SessionReady, VoiceAgentServerHost

    response_host = responses.ResponsesAgentServerHost
    if responses_first:

        class CombinedHost(response_host, VoiceAgentServerHost):
            pass

    else:

        class CombinedHost(VoiceAgentServerHost, response_host):
            pass

    set_resilient_tasks_enabled(enabled)
    host = CombinedHost(
        options=responses.ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    voice_seen = []
    responses_seen = []
    executed = []

    @task(name="voice_protocol_probe")
    async def probe(ctx: TaskContext[str]) -> str:
        executed.append(ctx.input)
        return ctx.input

    @host.on_session_start
    async def start(session, event):
        voice_seen.append(manager_available())
        if manager_available():
            run = await probe.start(task_id="voice-probe", input="ran")
            assert await run.result() == "ran"
        else:
            with pytest.raises(TaskManagerNotInitialized):
                await probe.start(task_id="voice-probe", input="must not run")
        await session.send(SessionReady())

    @host.response_handler
    async def response_handler(request, context, cancellation_signal):
        responses_seen.append(manager_available())
        events = responses.ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    with TestClient(host) as client:
        with client.websocket_connect(path) as websocket:
            websocket.send_json(
                {
                    "type": "session.start",
                    "id": "m_start",
                    "ts": "2026-10-15T00:00:00Z",
                    "protocol_version": "1.0",
                    "reconnect": False,
                    "response_timeouts": {"first_output_ms": 1000, "idle_ms": 1000, "max_duration_ms": 3000},
                }
            )
            assert websocket.receive_json()["type"] == "session.ready"
        assert voice_seen == [enabled]
        assert executed == (["ran"] if enabled else [])
        response = client.post("/responses", json={"input": "hello", "store": False})
        assert response.status_code == 200, response.text
        assert responses_seen == [resilient or steerable]


@pytest.mark.parametrize("enabled", [False, True])
def test_invocations_switch_controls_http_and_websocket(enabled: bool) -> None:
    set_resilient_tasks_enabled(enabled)
    host = InvocationAgentServerHost(configure_observability=None)

    @host.invoke_handler
    async def invoke(request):
        return JSONResponse({"task_runtime": manager_available()})

    @host.ws_handler
    async def websocket_handler(websocket):
        await websocket.send_json({"task_runtime": manager_available()})

    with TestClient(host) as client:
        assert client.post("/invocations", json={}).json() == {"task_runtime": enabled}
        with client.websocket_connect("/invocations_ws") as websocket:
            assert websocket.receive_json() == {"task_runtime": enabled}


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("responses_first", [False, True])
def test_composed_protocols_use_independent_enablement(
    enabled: bool, resilient: bool, steerable: bool, responses_first: bool
) -> None:
    responses = pytest.importorskip("azure.ai.agentserver.responses")
    response_host = responses.ResponsesAgentServerHost
    if responses_first:

        class CombinedHost(response_host, InvocationAgentServerHost):
            pass

    else:

        class CombinedHost(InvocationAgentServerHost, response_host):
            pass

    set_resilient_tasks_enabled(enabled)
    host = CombinedHost(
        options=responses.ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    assert resilient_tasks_enabled() is enabled
    observed: list[bool] = []

    @host.invoke_handler
    async def invoke(request):
        return JSONResponse({"task_runtime": manager_available()})

    @host.response_handler
    async def response_handler(request, context, cancellation_signal):
        observed.append(context._task_context is not None)
        assert manager_available() is (resilient or steerable)
        events = responses.ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    with TestClient(host) as client:
        assert (host._task_manager is not None) is (enabled or resilient or steerable)
        assert client.post("/invocations", json={}).json() == {"task_runtime": enabled}
        result = client.post("/responses", json={"input": "hello", "store": True})
        assert result.status_code == 200, result.text
        assert observed == [resilient or steerable]
        assert client.post("/invocations", json={}).json() == {"task_runtime": enabled}


@pytest.mark.parametrize("responses_first", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("multi_turn", [False, True])
@pytest.mark.parametrize("separate_hosts", [False, True])
@pytest.mark.asyncio
async def test_protocol_recovery_requires_enabled_owning_host(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    responses_first: bool,
    resilient: bool,
    steerable: bool,
    multi_turn: bool,
    separate_hosts: bool,
) -> None:
    responses = pytest.importorskip("azure.ai.agentserver.responses")
    from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager, _SCHEMA_VERSION, _SCHEMA_VERSION_KEY
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    from azure.ai.agentserver.responses import PlatformContext
    from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
    from azure.ai.agentserver.responses.hosting._task_id import derive_lifecycle_id
    from azure.ai.agentserver.responses.models._generated import CreateResponse, ResponseObject
    from azure.ai.agentserver.responses.store._file import FileResponseStore

    response_host = responses.ResponsesAgentServerHost
    if responses_first:

        class CombinedHost(response_host, InvocationAgentServerHost):
            pass

    else:

        class CombinedHost(InvocationAgentServerHost, response_host):
            pass

    task_store = LocalFileTaskProvider(tmp_path / "tasks")
    store = FileResponseStore(storage_dir=tmp_path / "responses")
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(lambda _: task_store))
    set_resilient_tasks_enabled(True)
    host_type = response_host if separate_hosts else CombinedHost
    host = host_type(
        options=responses.ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        store=store,
        configure_observability=None,
    )
    active_host = InvocationAgentServerHost(configure_observability=None) if separate_hosts else host
    invocation_ran = asyncio.Event()
    observed = []

    @task(name="invocations_recovery_control")
    async def invocation_work(ctx: TaskContext[str]) -> str:
        assert ctx.entry_mode == "recovered"
        assert get_task_manager() is active_host._task_manager
        invocation_ran.set()
        return "invocations still recover"

    @host.response_handler
    async def handler(request, context, cancellation_signal):
        observed.append((context.is_recovery, get_task_manager() is active_host._task_manager))
        events = responses.ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()

    response_id = "resp_disabled_protocol_recovery"
    platform_context = PlatformContext(user_id_key="owner")
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
    orchestrator = host._endpoint._orchestrator._resilient_orchestrator
    primitive = orchestrator._multi_turn_task_fn if multi_turn else orchestrator._one_shot_task_fn
    params = ResilientResponseInput(
        request=CreateResponse(model="m", input="old work", store=True, background=True, stream=False),
        response_id=response_id,
        disposition="re-invoke",
        user_id_key="owner",
    ).to_task_input()
    response_task_id = derive_lifecycle_id(response_id, "owner")
    for name, task_id, task_input in (
        (primitive.name, response_task_id, params),
        (invocation_work.name, "invocations-recovery-control", "continue"),
    ):
        payload = {"input": task_input, _SCHEMA_VERSION_KEY: _SCHEMA_VERSION}
        if multi_turn and name == primitive.name:
            payload["last_input_id"] = derive_lifecycle_id(response_id, "owner")
        info = await task_store.create(
            TaskCreateRequest(
                id=task_id,
                agent_name=host.config.agent_name or "default",
                session_id=host.config.session_id or "local",
                status="in_progress",
                title=name,
                payload=payload,
                tags={"task_name": name},
                source=TaskManager._build_source(name),
                lease_owner=derive_lease_owner(
                    host.config.agent_name or "unknown-agent", host.config.session_id or "local"
                ),
                lease_instance_id="interrupted-instance",
                lease_duration_seconds=60,
            )
        )
        info.lease.expires_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        task_store._write_task(info)
    before = await task_store.get(response_task_id)
    async with active_host.router.lifespan_context(active_host):
        await asyncio.wait_for(invocation_ran.wait(), timeout=5)
        if (resilient or steerable) and not separate_hosts:

            async def wait_for_terminal():
                while (await store.get_response(response_id, context=platform_context))["status"] == "in_progress":
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_terminal(), timeout=5)
            assert observed == [(True, True)]
            assert (await store.get_response(response_id, context=platform_context))["status"] == "completed"
        else:
            assert observed == []
            if separate_hosts:
                assert host._task_manager is None
            after = await task_store.get(response_task_id)
            assert after.status == before.status == "in_progress"
            assert after.etag == before.etag
            assert after.lease.instance_id == before.lease.instance_id == "interrupted-instance"
            assert after.lease.generation == before.lease.generation
            assert after.payload == before.payload
            assert (await store.get_response(response_id, context=platform_context))["status"] == "in_progress"
