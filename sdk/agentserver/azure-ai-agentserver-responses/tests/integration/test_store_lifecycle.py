# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Integration tests for store and lifecycle behavior."""

from __future__ import annotations

import asyncio
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from tests._helpers import poll_until


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire lifecycle integration tests."""

    async def _events():
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _cancellable_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then blocks until cancelled (Phase 3)."""

    async def _events():
        yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    return TestClient(app)


def test_store_lifecycle__create_read_and_cleanup_behavior() -> None:
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    read_response = client.get(f"/responses/{response_id}")
    assert read_response.status_code == 200

    # Lifecycle cleanup contract: after explicit cancellation, read should still be stable or terminally unavailable.
    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code in {200, 400}


def test_store_lifecycle__background_completion_is_observed_deterministically() -> None:
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": True,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    terminal_states = {"completed", "failed", "incomplete", "cancelled"}
    latest_status: str | None = None

    def _is_terminal() -> bool:
        nonlocal latest_status
        get_response = client.get(f"/responses/{response_id}")
        if get_response.status_code != 200:
            return False
        latest_status = get_response.json().get("status")
        return latest_status in terminal_states

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: {"last_status": latest_status},
        label="background completion polling",
    )
    assert ok, failure


def test_store_lifecycle__background_cancel_transition_is_deterministic() -> None:
    app = ResponsesAgentServerHost()
    app.response_handler(_cancellable_bg_handler)
    client = TestClient(app)

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": True,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json().get("status") == "cancelled"

    latest_status: str | None = None

    def _is_cancelled() -> bool:
        nonlocal latest_status
        get_response = client.get(f"/responses/{response_id}")
        if get_response.status_code != 200:
            return False
        latest_status = get_response.json().get("status")
        return latest_status == "cancelled"

    ok, failure = poll_until(
        _is_cancelled,
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: {"last_status": latest_status},
        label="background cancel transition polling",
    )
    assert ok, failure
