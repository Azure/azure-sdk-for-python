# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: a resilient task-start failure must FAIL the request.

When the resilient-task subsystem IS installed (hosted) but starting the
task-backed background execution fails, the server must NOT silently degrade
to a non-durable, connection-scoped ``asyncio.create_task`` (which loses crash
recovery while looking healthy). Instead it must fail immediately and surface
the failure as a *platform* error source — exactly like a Foundry storage
failure.

The legitimate "no task subsystem at all" case (e.g. a test client without a
TaskManager) must STILL run the handler in-process — that is not a failure.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core._platform_headers import ERROR_DETAIL, ERROR_SOURCE
from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.hosting import _orchestrator as _orch
from azure.ai.agentserver.responses.hosting import _resilient_orchestrator as _ro
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


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
    """Regression: no task subsystem (non-hosted) → handler runs in-process."""

    def test_no_manager_background_runs_handler_ok(self) -> None:
        # Plain TestClient (no `with` → no lifespan → no TaskManager installed)
        # and non-hosted (FOUNDRY_HOSTING_ENVIRONMENT unset) → legitimate
        # in-process fallback, NOT a failure.
        client = _build_client()
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert resp.status_code == 200, resp.text
        assert ERROR_SOURCE not in resp.headers


class TestHostedNoTaskManagerFailsLoudly:
    """Hosted + no manager → durability is mandatory → fail as platform error.

    In a hosted deployment the resilient-task subsystem is auto-initialized
    with no opt-out, so its absence is a platform-infrastructure failure — the
    server must NOT silently degrade a ``store=true`` response to a non-durable
    in-process run.
    """

    def test_hosted_no_manager_background_fails_platform_500(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Simulate hosted at the gate (no real env change → no Foundry store
        # auto-activation) while the bare TestClient has no manager installed.
        monkeypatch.setattr(_orch, "_is_hosted_environment", lambda: True)
        client = _build_client()
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hi", "stream": False, "store": True, "background": True},
        )
        assert resp.status_code == 500, resp.text
        assert resp.headers.get(ERROR_SOURCE) == "platform"
        assert ERROR_DETAIL in resp.headers
        assert "in_progress" not in resp.text

    def test_hosted_no_manager_streaming_emits_error_event(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_orch, "_is_hosted_environment", lambda: True)
        client = _build_client()
        resp = client.post(
            "/responses",
            json={"model": "test", "input": "hi", "stream": True, "store": True, "background": True},
        )
        types = [e["type"] for e in _collect_sse_events(resp.text)]
        assert "error" in types, f"expected a standalone error event, got: {types}"
        assert "response.completed" not in types, f"must not complete, got: {types}"
