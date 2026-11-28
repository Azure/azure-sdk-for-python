# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Snapshot activation preserves independent protocol task-runtime requirements."""

from __future__ import annotations

from unittest.mock import Mock

import httpx
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
from azure.ai.agentserver.core.tasks import _decorator
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, get_task_manager
from azure.ai.agentserver.responses import ResponseEventStream, ResponsesAgentServerHost, ResponsesServerOptions


@pytest.fixture(autouse=True)
def snapshot_runtime(monkeypatch, tmp_path):
    definitions = list(_decorator._REGISTERED_DESCRIPTORS)
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "snapshot-protocol")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "snapshot-session")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    monkeypatch.setenv("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", "0")
    provider = LocalFileTaskProvider(tmp_path / "tasks")
    factory = Mock(return_value=provider)
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(factory))
    try:
        yield factory
    finally:
        _decorator._REGISTERED_DESCRIPTORS[:] = definitions


def restore_payload():
    return {
        "session_context": {
            "session_id": "snapshot-session",
            "restore_id": "snapshot-restore",
            "session_env_overrides": {"FOUNDRY_AGENT_SESSION_GUID": "a" * 32},
        }
    }


def manager_available():
    try:
        get_task_manager()
        return True
    except TaskManagerNotInitialized:
        return False


def snapshot_mode(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)


def combined_type(invocations_type, responses_first):
    if responses_first:

        class CombinedHost(ResponsesAgentServerHost, invocations_type):
            pass

    else:

        class CombinedHost(invocations_type, ResponsesAgentServerHost):
            pass

    return CombinedHost


def register_response_probe(host, observed):
    @host.response_handler
    async def response_handler(request, context, cancellation_signal):
        observed.append(manager_available())
        events = ResponseEventStream(response_id=context.response_id, request=request)
        yield events.emit_created()
        yield events.emit_completed()


@pytest.mark.parametrize("value", [None, "false", "true"])
@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
def test_responses_snapshot_uses_options_not_invocations_switch(
    monkeypatch, snapshot_runtime, value, switch, resilient, steerable
):
    snapshot_mode(monkeypatch, value)
    set_resilient_tasks_enabled(switch)
    enabled = resilient or steerable
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    observed, executed = [], []
    register_response_probe(host, observed)
    callbacks = 0

    @task(name="snapshot_callback_probe")
    async def probe(ctx: TaskContext[str]) -> str:
        executed.append(ctx.input)
        return ctx.input

    @host.after_restore_handler
    async def restored(context):
        nonlocal callbacks
        callbacks += 1
        assert manager_available() is enabled
        if enabled:
            manager = get_task_manager()
            orchestrator = host._endpoint._orchestrator._resilient_orchestrator
            for primitive in (orchestrator._one_shot_task_fn, orchestrator._multi_turn_task_fn):
                assert manager._resume_callbacks[primitive.name] is primitive._fn
                assert manager._resume_opts[primitive.name] is primitive._opts
            if value == "true":
                assert not manager._startup_phases["recovery"].completed
                assert manager._periodic_recovery_task is None
            assert await probe.run(input=context.session_id) == "snapshot-session"
        else:
            with pytest.raises(TaskManagerNotInitialized):
                await probe.start(input=context.session_id)

    assert resilient_tasks_enabled() is switch
    with TestClient(host) as client:
        assert (host._task_manager is not None) is (enabled and value != "true")
        if value == "true":
            snapshot_runtime.assert_not_called()
            assert client.post("/_agent/before-snapshot", json={}).status_code == 200
            snapshot_runtime.assert_not_called()
        first = client.post("/_agent/after-restore", json=restore_payload())
        assert first.status_code == 200, first.text
        manager = host._task_manager
        assert client.post("/_agent/after-restore", json=restore_payload()).status_code == 200
        assert host._task_manager is manager
        assert callbacks == 1
        assert executed == (["snapshot-session"] if enabled else [])
        assert client.post("/responses", json={"input": "probe", "store": False}).status_code == 200
        assert observed == [enabled]
        if enabled:
            assert manager._startup_phases["ready"].completed
            assert manager._periodic_recovery_task is not None
            assert not manager._periodic_recovery_task.done()
            snapshot_runtime.assert_called_once()
        else:
            snapshot_runtime.assert_not_called()
    assert host._task_manager is None
    assert resilient_tasks_enabled() is switch


@pytest.mark.parametrize("value", [None, "false", "true"])
@pytest.mark.parametrize("enabled", [False, True])
def test_invocations_snapshot_switch_controls_http_and_websocket(monkeypatch, value, enabled):
    invocations = pytest.importorskip("azure.ai.agentserver.invocations")
    snapshot_mode(monkeypatch, value)
    set_resilient_tasks_enabled(enabled)
    host = invocations.InvocationAgentServerHost(configure_observability=None)

    @host.invoke_handler
    async def invoked(request):
        return JSONResponse({"enabled": manager_available()})

    @host.ws_handler
    async def websocket(websocket):
        await websocket.send_json({"enabled": manager_available()})

    with TestClient(host) as client:
        assert (host._task_manager is not None) is (enabled and value != "true")
        assert client.post("/_agent/after-restore", json=restore_payload()).status_code == 200
        assert client.post("/invocations", json={}).json() == {"enabled": enabled}
        with client.websocket_connect("/invocations_ws") as websocket:
            assert websocket.receive_json() == {"enabled": enabled}


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("resilient,steerable", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("responses_first", [False, True])
def test_composed_snapshot_preserves_protocol_access(
    monkeypatch, snapshot_runtime, switch, resilient, steerable, responses_first
):
    invocations = pytest.importorskip("azure.ai.agentserver.invocations")
    snapshot_mode(monkeypatch, "true")
    set_resilient_tasks_enabled(switch)
    host = combined_type(invocations.InvocationAgentServerHost, responses_first)(
        options=ResponsesServerOptions(resilient_background=resilient, steerable_conversations=steerable),
        configure_observability=None,
    )
    observed = []
    register_response_probe(host, observed)

    @host.invoke_handler
    async def invoked(request):
        return JSONResponse({"enabled": manager_available()})

    @host.ws_handler
    async def websocket(websocket):
        await websocket.send_json({"enabled": manager_available()})

    with TestClient(host) as client:
        snapshot_runtime.assert_not_called()
        assert host._task_manager is None
        assert client.post("/_agent/after-restore", json=restore_payload()).status_code == 200
        assert (host._task_manager is not None) is (switch or resilient or steerable)
        assert client.post("/invocations", json={}).json() == {"enabled": switch}
        with client.websocket_connect("/invocations_ws") as websocket:
            assert websocket.receive_json() == {"enabled": switch}
        assert client.post("/responses", json={"input": "probe", "store": False}).status_code == 200
        assert observed == [resilient or steerable]
        assert client.post("/_agent/after-restore", json=restore_payload()).status_code == 200
        assert snapshot_runtime.call_count == int(switch or resilient or steerable)
    assert resilient_tasks_enabled() is switch


@pytest.mark.parametrize("switch,responses_enabled", [(False, False), (False, True), (True, False), (True, True)])
@pytest.mark.parametrize("responses_first", [False, True])
@pytest.mark.parametrize("path", ["/invocations_ws", "/voice_conversation_engine"])
def test_voice_snapshot_does_not_inherit_responses_opt_in(
    monkeypatch, switch, responses_enabled, responses_first, path
):
    voice = pytest.importorskip("azure.ai.agentserver.invocations.voice")
    snapshot_mode(monkeypatch, "true")
    set_resilient_tasks_enabled(switch)
    host = combined_type(voice.VoiceAgentServerHost, responses_first)(
        options=ResponsesServerOptions(resilient_background=responses_enabled), configure_observability=None
    )
    observed = []

    @host.on_session_start
    async def start(session, event):
        observed.append(manager_available())
        await session.send(voice.SessionReady())

    with TestClient(host) as client:
        assert host._task_manager is None
        assert client.post("/_agent/after-restore", json=restore_payload()).status_code == 200
        with client.websocket_connect(path) as websocket:
            websocket.send_json(
                {
                    "type": "session.start",
                    "id": "snapshot-start",
                    "ts": "2026-10-26T00:00:00Z",
                    "protocol_version": "1.0",
                    "reconnect": False,
                    "response_timeouts": {"first_output_ms": 1000, "idle_ms": 1000, "max_duration_ms": 3000},
                }
            )
            assert websocket.receive_json()["type"] == "session.ready"
        assert observed == [switch]


@pytest.mark.asyncio
async def test_overlapping_snapshot_hosts_keep_own_runtime(monkeypatch, tmp_path):
    snapshot_mode(monkeypatch, "true")
    providers = iter([LocalFileTaskProvider(tmp_path / "first"), LocalFileTaskProvider(tmp_path / "second")])
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(lambda _: next(providers)))
    set_resilient_tasks_enabled(False)
    first = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=True), configure_observability=None
    )
    second = ResponsesAgentServerHost(
        options=ResponsesServerOptions(steerable_conversations=True), configure_observability=None
    )
    async with first.router.lifespan_context(first):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=first), base_url="http://test") as client:
            assert (await client.post("/_agent/after-restore", json=restore_payload())).status_code == 200
            first_manager = get_task_manager()
            async with second.router.lifespan_context(second):
                async with httpx.AsyncClient(
                    transport=httpx.ASGITransport(app=second), base_url="http://test"
                ) as other:
                    assert (await other.post("/_agent/after-restore", json=restore_payload())).status_code == 200
                    second_manager = get_task_manager()
                    assert second_manager is not first_manager
                    assert (await client.post("/_agent/after-restore", json=restore_payload())).status_code == 200
                    assert get_task_manager() is second_manager
            assert get_task_manager() is first_manager
            assert first._task_manager is first_manager
    assert first._task_manager is second._task_manager is None
