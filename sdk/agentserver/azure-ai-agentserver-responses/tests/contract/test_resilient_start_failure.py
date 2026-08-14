# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: resilient task-start behavior.

Two distinct cases with DIFFERENT contracts:

1. The resilient-task subsystem IS installed but starting the task-backed
   execution *fails* (the start call raises): the server must NOT silently
   degrade to a non-durable ``asyncio.create_task`` — it must fail immediately
   and surface a *platform* error source (like a Foundry storage failure). A
   real durability failure must not hide behind a healthy-looking response.

2. No task subsystem is installed at all (the host did not enable resilient
   tasks via ``set_resilient_tasks_enabled``): this is the deliberate opt-out
   path. ``TaskManagerNotInitialized`` is SWALLOWED and the handler runs
   in-process — the response still executes and persists (GET works), it is
   simply not crash-recoverable. This applies regardless of hosted vs local.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core._platform_headers import ERROR_DETAIL, ERROR_SOURCE
from azure.ai.agentserver.core.tasks import (
    TaskManagerNotInitialized,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
)
from azure.ai.agentserver.core.tasks._manager import get_task_manager
from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as _ro
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


@pytest.fixture()
def _switch_off() -> Any:
    """Ensure the process-global resilient-tasks state is OFF for the test.

    Both the enable switch and the ``TaskManager`` singleton are process-global
    and other tests in a shared pytest process may have flipped the switch on or
    installed a manager (e.g. by constructing a ``resilient_background=True``
    host). Snapshot, reset both to the switch-off / no-manager state so the
    production opt-out path is genuinely exercised, then restore afterwards.
    """
    from azure.ai.agentserver.core.tasks import _manager as _mgr_mod  # pylint: disable=import-outside-toplevel
    from azure.ai.agentserver.core.tasks._manager import set_task_manager  # pylint: disable=import-outside-toplevel

    saved_flag = resilient_tasks_enabled()
    saved_mgr = _mgr_mod._manager  # noqa: SLF001  # pylint: disable=protected-access
    set_resilient_tasks_enabled(False)
    set_task_manager(None)
    try:
        yield
    finally:
        set_task_manager(saved_mgr)
        set_resilient_tasks_enabled(saved_flag)


async def _noop_handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> AsyncIterator[Any]:
    async def _events() -> AsyncIterator[Any]:
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None) or "")
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _build_client(handler: Any = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


@pytest.fixture()
def _start_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the resilient task START to fail (subsystem present but start raises)."""

    async def _boom(self: Any, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Simulated task-store failure")

    monkeypatch.setattr(_ro.ResilientResponseOrchestrator, "start_resilient", _boom)


def _collect_sse_events(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for line in text.splitlines():
        if not line:
            if current_type is not None:
                events.append({"type": current_type, "data": json.loads(current_data) if current_data else {}})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type is not None:
        events.append({"type": current_type, "data": json.loads(current_data) if current_data else {}})
    return events


class TestTaskStartFailureSurfacesPlatform:
    """Manager present + task start fails → fail immediately, platform source."""

    def test_background_start_failure_returns_platform_500(self, _start_fails: None) -> None:
        with _build_client() as client:  # lifespan installs a real TaskManager
            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": False, "store": True, "background": True},
            )
        assert resp.status_code == 500, resp.text
        assert resp.headers.get(ERROR_SOURCE) == "platform"
        assert ERROR_DETAIL in resp.headers
        # Must NOT have silently degraded to a healthy-looking in_progress 200.
        assert "in_progress" not in resp.text

    def test_sync_start_failure_returns_platform_500(self, _start_fails: None) -> None:
        with _build_client() as client:
            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": False, "store": True, "background": False},
            )
        assert resp.status_code == 500, resp.text
        assert resp.headers.get(ERROR_SOURCE) == "platform"
        assert ERROR_DETAIL in resp.headers

    def test_streaming_start_failure_emits_standalone_error_event(self, _start_fails: None) -> None:
        with _build_client() as client:
            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": True, "store": True, "background": True},
            )
        events = _collect_sse_events(resp.text)
        types = [e["type"] for e in events]
        # Streaming-native failure surface: a standalone `error` event, and the
        # response must NOT look like it completed successfully.
        assert "error" in types, f"expected a standalone error event, got: {types}"
        assert "response.completed" not in types, f"must not complete on start failure, got: {types}"


class TestNoTaskManagerStillRunsHandler:
    """No task subsystem (opt-out) → handler runs in-process (non-durable)."""

    def test_no_manager_background_runs_handler_ok(self) -> None:
        # Plain TestClient (no `with` → no lifespan → no TaskManager installed)
        # → the outer catch swallows TaskManagerNotInitialized and runs the
        # handler in-process. Legitimate opt-out path, NOT a failure.
        client = _build_client()
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert resp.status_code == 200, resp.text
        assert ERROR_SOURCE not in resp.headers


class TestNoTaskManagerSwallowsAndRunsInProcess:
    """Recovery is opt-in: with the switch OFF, the ASGI lifespan installs NO
    TaskManager, so ``store=true`` work is NOT failed as a platform error — the
    outer catch swallows ``TaskManagerNotInitialized`` and runs the handler
    in-process (non-durable). The response still executes AND persists (GET
    works). Enabling durability is the operator's explicit choice via
    ``set_resilient_tasks_enabled(True)`` / ``resilient_background``."""

    def test_switch_off_no_manager_installed_and_response_completes(self, _switch_off: Any) -> None:
        # Enter the lifespan with the switch explicitly OFF so this exercises the
        # real production opt-out path (not the bare no-lifespan test client).
        with _build_client() as client:
            # Lifespan ran but installed NO manager (switch off).
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": False, "store": True, "background": True},
            )
            assert resp.status_code == 200, resp.text
            # Swallowed → not a platform error.
            assert ERROR_SOURCE not in resp.headers
            response_id = resp.json()["id"]

            # The in-process fallback runs AND persists: GET reaches a terminal.
            import time

            deadline = time.monotonic() + 10.0
            status = None
            while time.monotonic() < deadline:
                got = client.get(f"/responses/{response_id}")
                if got.status_code == 200:
                    status = got.json().get("status")
                    if status in ("completed", "failed", "cancelled"):
                        break
                time.sleep(0.05)
            assert status == "completed", f"expected completed via in-process fallback, got {status}"

    def test_switch_off_no_manager_streaming_runs_in_process(self, _switch_off: Any) -> None:
        with _build_client() as client:
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": True, "store": True, "background": True},
            )
            types = [e["type"] for e in _collect_sse_events(resp.text)]
            # In-process fallback runs the handler to completion; no error surface.
            assert "error" not in types, f"must not surface an error on opt-out, got: {types}"
            assert "response.completed" in types, f"expected completion, got: {types}"
