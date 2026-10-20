# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Responses feature activation is independent of the Invocations switch."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
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
