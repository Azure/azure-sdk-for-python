# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for DELETE /responses/{response_id} endpoint behavior."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from tests._helpers import EventGate, poll_until


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire the hosting surface in contract tests."""

    async def _events():
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _delayed_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that keeps background execution in-flight for deterministic delete checks."""

    async def _events():
        if cancellation_signal.is_set():
            return
        await asyncio.sleep(0.5)
        if cancellation_signal.is_set():
            return
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _build_client(handler: Any | None = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_response_handler)
    return TestClient(app)


def _throwing_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Background handler that raises immediately — produces status=failed."""

    async def _events():
        raise RuntimeError("Simulated handler failure")
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _throwing_after_created_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Background handler that emits response.created then raises — produces status=failed.

    Phase 3: by yielding response.created first, the POST returns HTTP 200 instead of 500.
    """

    async def _events():
        yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
        raise RuntimeError("Simulated handler failure")

    return _events()


def _cancellable_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then blocks until cancelled (Phase 3)."""

    async def _events():
        yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _incomplete_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Background handler that emits an incomplete terminal event."""

    async def _events():
        yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
        yield {"type": "response.incomplete", "response": {"status": "incomplete", "output": []}}

    return _events()


def test_delete__deletes_stored_completed_response() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload.get("id") == response_id
    assert payload.get("object") == "response"
    assert payload.get("deleted") is True


def test_delete__returns_400_for_background_in_flight_response() -> None:
    client = _build_client(_cancellable_bg_handler)

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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 400
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("message") == "Cannot delete an in-flight response."


def test_delete__returns_404_for_unknown_response_id() -> None:
    client = _build_client()

    delete_response = client.delete("/responses/resp_does_not_exist")
    assert delete_response.status_code == 404
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"


def test_delete__returns_404_for_store_false_response() -> None:
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": False,
            "background": False,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 404
    payload = delete_response.json()
    assert payload["error"].get("type") == "invalid_request_error"


def test_delete__get_returns_400_after_deletion() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 400
    payload = get_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert "deleted" in (payload["error"].get("message") or "").lower()


def test_delete__cancel_returns_404_after_deletion() -> None:
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

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 404
    payload = cancel_response.json()
    assert payload["error"].get("type") == "invalid_request_error"


def _make_blocking_sync_response_handler(started_gate: EventGate, release_gate: threading.Event):
    """Factory for a handler that holds a sync request in-flight for concurrent operation tests."""

    def _handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            started_gate.signal(True)
            while not release_gate.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)
            if False:  # pragma: no cover
                yield None

        return _events()

    return _handler


def test_delete__returns_404_for_non_bg_in_flight_response() -> None:
    """FR-024 — Non-background in-flight responses are not findable → DELETE 404."""
    started_gate = EventGate()
    release_gate = threading.Event()
    handler = _make_blocking_sync_response_handler(started_gate, release_gate)
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    client = TestClient(app)
    response_id = IdGenerator.new_response_id()

    create_result: dict[str, Any] = {}

    def _do_create() -> None:
        try:
            create_result["response"] = client.post(
                "/responses",
                json={
                    "response_id": response_id,
                    "model": "gpt-4o-mini",
                    "input": "hello",
                    "stream": False,
                    "store": True,
                    "background": False,
                },
            )
        except Exception as exc:  # pragma: no cover
            create_result["error"] = exc

    t = threading.Thread(target=_do_create, daemon=True)
    t.start()

    started, _ = started_gate.wait(timeout_s=2.0)
    assert started, "Expected sync create to enter handler before DELETE"

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 404

    release_gate.set()
    t.join(timeout=2.0)
    assert not t.is_alive()


# ══════════════════════════════════════════════════════════
# B6: DELETE on terminal statuses (failed / incomplete / cancelled)
# ══════════════════════════════════════════════════════════


def test_delete__deletes_stored_failed_response() -> None:
    """B6 — DELETE on a failed (terminal) stored response returns 200 with deleted=True."""
    client = _build_client(_throwing_after_created_bg_handler)

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

    ok, failure = poll_until(
        lambda: client.get(f"/responses/{response_id}").json().get("status") == "failed",
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: client.get(f"/responses/{response_id}").json().get("status"),
        label=f"status=failed for {response_id}",
    )
    assert ok, failure

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload.get("id") == response_id
    assert payload.get("object") == "response"
    assert payload.get("deleted") is True


def test_delete__deletes_stored_incomplete_response() -> None:
    """B6 — DELETE on an incomplete (terminal) stored response returns 200 with deleted=True."""
    client = _build_client(_incomplete_bg_handler)

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

    ok, failure = poll_until(
        lambda: client.get(f"/responses/{response_id}").json().get("status") == "incomplete",
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: client.get(f"/responses/{response_id}").json().get("status"),
        label=f"status=incomplete for {response_id}",
    )
    assert ok, failure

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload.get("id") == response_id
    assert payload.get("object") == "response"
    assert payload.get("deleted") is True


def test_delete__deletes_stored_cancelled_response() -> None:
    """B6 — DELETE on a cancelled (terminal) stored response returns 200 with deleted=True."""
    client = _build_client(_cancellable_bg_handler)

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

    ok, failure = poll_until(
        lambda: client.get(f"/responses/{response_id}").json().get("status") == "cancelled",
        timeout_s=5.0,
        interval_s=0.05,
        context_provider=lambda: client.get(f"/responses/{response_id}").json().get("status"),
        label=f"status=cancelled for {response_id}",
    )
    assert ok, failure

    delete_response = client.delete(f"/responses/{response_id}")
    assert delete_response.status_code == 200
    payload = delete_response.json()
    assert payload.get("id") == response_id
    assert payload.get("object") == "response"
    assert payload.get("deleted") is True


# ══════════════════════════════════════════════════════════
# N-5: Second DELETE on already-deleted response → 404
# ══════════════════════════════════════════════════════════


def test_delete__second_delete_returns_404() -> None:
    """FR-024 — Deletion is permanent; a second DELETE on an already-deleted ID returns 404."""
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

    # First DELETE – should succeed
    first_delete = client.delete(f"/responses/{response_id}")
    assert first_delete.status_code == 200

    # Second DELETE – response is gone, must return 404
    second_delete = client.delete(f"/responses/{response_id}")
    assert second_delete.status_code == 404, (
        "Second DELETE on an already-deleted response must return 404 (response no longer exists)"
    )
    payload = second_delete.json()
    assert payload["error"].get("type") == "invalid_request_error"


def test_delete__deletes_completed_background_response() -> None:
    """DELETE a completed background response returns 200 with deletion confirmation."""
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

    # Wait for background task to complete
    ok, _ = poll_until(
        lambda: (
            client.get(f"/responses/{response_id}").json().get("status")
            in {
                "completed",
                "failed",
            }
        ),
        timeout_s=5.0,
        interval_s=0.05,
        label="wait for bg completion",
    )
    assert ok, "Background response did not reach terminal state within timeout"

    delete = client.delete(f"/responses/{response_id}")
    assert delete.status_code == 200
    payload = delete.json()
    assert payload["id"] == response_id
    assert payload["deleted"] is True
    assert payload.get("object") == "response", (
        f"DELETE result must have object='response', got: {payload.get('object')}"
    )
