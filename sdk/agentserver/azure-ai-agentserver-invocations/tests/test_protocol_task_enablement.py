# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Invocations enablement must remain independent of Responses features."""

from __future__ import annotations

import pytest
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import (
    TaskManagerNotInitialized,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
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
