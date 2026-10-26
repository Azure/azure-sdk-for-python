# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: resilient task-start behavior.

Two distinct cases with DIFFERENT contracts:

1. The resilient-task subsystem IS installed but starting the task-backed
   execution *fails* (the start call raises): the server must NOT silently
   degrade to a non-durable ``asyncio.create_task`` — it must fail immediately
   and surface a *platform* error source (like a Foundry storage failure). A
   real durability failure must not hide behind a healthy-looking response.

2. Neither Responses runtime option is enabled: this is the deliberate opt-out
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
from azure.ai.agentserver.core.tasks._manager import get_task_manager, set_task_manager
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as _ro
from azure.ai.agentserver.responses.hosting._runtime_state import _RuntimeState
from azure.ai.agentserver.responses.models.runtime import ResponseExecution
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


@pytest.fixture()
def _switch_off() -> Any:
    """Ensure the process-global resilient-tasks state is OFF for the test.

    Both the enable switch and the ``TaskManager`` singleton are process-global
    and other tests in a shared pytest process may have flipped the switch on or
    installed a manager (e.g. by starting an enabled Responses host).
    Snapshot, reset both to the switch-off / no-manager state so the
    production opt-out path is genuinely exercised, then restore afterwards.
    """
    from azure.ai.agentserver.core.tasks import _manager as _mgr_mod  # pylint: disable=import-outside-toplevel

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


def _build_client(handler: Any = None, *, task_runtime: bool = False, resilient_background: bool = False) -> TestClient:
    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(steerable_conversations=task_runtime, resilient_background=resilient_background)
    )
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
        with _build_client(task_runtime=True) as client:  # lifespan installs a real TaskManager
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
        with _build_client(task_runtime=True) as client:
            resp = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": False, "store": True, "background": False},
            )
        assert resp.status_code == 500, resp.text
        assert resp.headers.get(ERROR_SOURCE) == "platform"
        assert ERROR_DETAIL in resp.headers

    def test_streaming_start_failure_emits_standalone_error_event(self, _start_fails: None) -> None:
        with _build_client(task_runtime=True) as client:
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

    @pytest.mark.parametrize("stream", [False, True])
    @pytest.mark.parametrize("resilient,steerable", [(False, True), (True, False), (True, True)])
    def test_closed_manager_never_falls_back_to_non_durable_execution(
        self, _switch_off: Any, caplog: pytest.LogCaptureFixture, stream: bool, resilient: bool, steerable: bool
    ) -> None:
        called = []

        async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
            called.append(True)
            return await _noop_handler(request, context, cancellation_signal)

        with _build_client(handler, task_runtime=steerable, resilient_background=resilient) as client:
            manager = get_task_manager()
            assert client.portal is not None
            client.portal.call(manager._shutdown_event.set)
            response = client.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": stream, "store": True},
            )
            if stream:
                types = [event["type"] for event in _collect_sse_events(response.text)]
                assert "error" in types
                assert "response.completed" not in types
            else:
                assert response.status_code == 500, response.text
                assert response.headers.get(ERROR_SOURCE) == "platform"
            assert not called
            assert any(
                record.exc_info and "TaskManager is shutting down" in str(record.exc_info[1])
                for record in caplog.records
            )


class TestNoTaskManagerStillRunsHandler:
    """No task subsystem (opt-out) → handler runs in-process (non-durable)."""

    def test_no_manager_background_runs_handler_ok(self, _switch_off: Any) -> None:
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
    """Recovery is opt-in: when no ``TaskManager`` is installed, ``store=true``
    work is NOT failed as a platform error — the responses outer catch swallows
    ``TaskManagerNotInitialized`` and runs the handler in-process (non-durable).
    The response still executes AND persists (GET works).

    These tests exercise the responses **swallow** behavior specifically. The
    no-manager condition is forced deterministically via ``set_task_manager(None)``
    inside the running lifespan so the test does not depend on process-global
    state left by other tests, nor on which core build performs (or skips) the
    manager construction — that gating is covered by the core opt-in tests."""

    def test_switch_off_no_manager_installed_and_response_completes(self, _switch_off: Any) -> None:
        with _build_client() as client:
            # Force the switch-off condition deterministically: whatever the
            # lifespan installed, ensure no manager is present so the responses
            # swallow path is the one under test.
            set_task_manager(None)
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
            # Force the switch-off condition deterministically (see above).
            set_task_manager(None)
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


class TestSnapshotTaskActivation:
    """Task definitions stay process-side; requests follow session activation."""

    def test_enabled_cold_start_installs_task_runtime(self, _switch_off: Any) -> None:
        with _build_client(task_runtime=True):
            assert get_task_manager() is not None
            assert not resilient_tasks_enabled()

    @pytest.mark.parametrize("background", [False, True])
    @pytest.mark.parametrize("user_id", [None, "snapshot-user"])
    @pytest.mark.parametrize("resilient,steerable", [(False, True), (True, False), (True, True)])
    def test_deferred_start_failure_removes_scoped_runtime(
        self,
        _switch_off: Any,
        monkeypatch: pytest.MonkeyPatch,
        background: bool,
        user_id: str | None,
        resilient: bool,
        steerable: bool,
    ) -> None:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", "true")
        registered: list[tuple[_RuntimeState, ResponseExecution]] = []
        original_add = _RuntimeState.add

        async def observe_add(
            state: _RuntimeState,
            record: ResponseExecution,
            *,
            expected_record: ResponseExecution | None = None,
        ) -> bool:
            registered.append((state, record))
            return await original_add(state, record, expected_record=expected_record)

        monkeypatch.setattr(_RuntimeState, "add", observe_add)
        called: list[bool] = []

        async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
            called.append(True)
            return await _noop_handler(request, context, cancellation_signal)

        headers = {"x-agent-user-id": user_id} if user_id is not None else {}
        with _build_client(handler, task_runtime=steerable, resilient_background=resilient) as http:
            response = http.post(
                "/responses",
                headers=headers,
                json={"model": "test", "input": "hi", "stream": False, "store": True, "background": background},
            )
            assert response.status_code == 500, response.text
            assert response.headers.get(ERROR_SOURCE) == "platform"
            assert not called
            assert len(registered) == 1
            state, record = registered[0]
            assert record.user_id_key == user_id
            assert http.portal is not None
            assert http.portal.call(state.get, record.response_id, user_id) is None
            assert http.portal.call(state.is_deleted, record.response_id, user_id)
            assert not http.portal.call(state.is_deleted, record.response_id, "unrelated-user")
            assert http.get(f"/responses/{record.response_id}", headers=headers).status_code == 404

    @pytest.mark.parametrize("stream", [False, True])
    @pytest.mark.parametrize("resilient,steerable", [(False, True), (True, False), (True, True)])
    def test_enabled_missing_runtime_does_not_fall_back(
        self, _switch_off: Any, monkeypatch: pytest.MonkeyPatch, stream: bool, resilient: bool, steerable: bool
    ) -> None:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", "true")
        called: list[bool] = []

        async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
            called.append(True)
            return await _noop_handler(request, context, cancellation_signal)

        with _build_client(handler, task_runtime=steerable, resilient_background=resilient) as http:
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()
            response = http.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": stream, "store": True},
            )
            if stream:
                types = [event["type"] for event in _collect_sse_events(response.text)]
                assert "error" in types
                assert "response.completed" not in types
            else:
                assert response.status_code == 500, response.text
                assert response.headers.get(ERROR_SOURCE) == "platform"
            assert not called

    @pytest.mark.parametrize("value", [None, "false"])
    @pytest.mark.parametrize("stream", [False, True])
    def test_cold_start_missing_runtime_keeps_in_process_fallback(
        self, _switch_off: Any, monkeypatch: pytest.MonkeyPatch, value: str | None, stream: bool
    ) -> None:
        if value is None:
            monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
        else:
            monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
        called: list[bool] = []

        async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event) -> Any:
            called.append(True)
            return await _noop_handler(request, context, cancellation_signal)

        # Plain TestClient (no `with`): the lifespan never runs, so no manager exists.
        response = _build_client(handler, task_runtime=True).post(
            "/responses",
            json={"model": "test", "input": "hi", "stream": stream, "store": True},
        )
        assert response.status_code == 200, response.text
        assert ERROR_SOURCE not in response.headers
        if stream:
            types = [event["type"] for event in _collect_sse_events(response.text)]
            assert "error" not in types
            assert "response.completed" in types
        assert called

    def test_requests_after_restore_use_registered_task_runtime(
        self, _switch_off: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("FOUNDRY_AGENT_SESSION_ID", raising=False)
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", "true")
        with _build_client(task_runtime=True) as http:
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()
            restored = http.post(
                "/_agent/after-restore",
                json={
                    "session_context": {
                        "session_id": "restored-session",
                        "restore_id": "restore-1",
                        "session_env_overrides": {},
                    }
                },
            )
            assert restored.status_code == 200, restored.text
            manager = get_task_manager()
            assert manager._config.session_id == "restored-session"
            assert {
                "responses_resilient_one_shot",
                "responses_resilient_multi_turn",
            }.issubset(manager._resume_callbacks)
            response = http.post(
                "/responses",
                json={"model": "test", "input": "hi", "stream": False, "store": True},
            )
            assert response.status_code == 200, response.text
            assert response.json()["status"] == "completed"
            assert ERROR_SOURCE not in response.headers
