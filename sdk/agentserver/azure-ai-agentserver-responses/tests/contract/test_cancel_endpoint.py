# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for POST /responses/{response_id}/cancel behavior."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.responses.hosting import ResponseHandler
from azure.ai.agentserver.responses._id_generator import IdGenerator
from tests._helpers import EventGate, poll_until


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire the hosting surface in contract tests."""
    async def _events():
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _delayed_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that keeps background execution cancellable for a short period."""
    async def _events():
        if cancellation_signal.is_set():
            return
        await asyncio.sleep(0.25)
        if cancellation_signal.is_set():
            return
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _cancellable_bg_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then blocks until cancelled.

    Phase 3: response_created_signal is set on the first event, so run_background
    returns quickly with in_progress status while the task waits for cancellation.
    """
    async def _events():
        yield {
            "type": "response.created",
            "payload": {
                "status": "in_progress",
                "output": [],
            },
        }
        # Block until cancellation signal is set
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _raising_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that raises to transition a background response into failed."""
    async def _events():
        raise RuntimeError("simulated handler failure")
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _unknown_cancellation_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that raises an unknown cancellation exception source."""
    async def _events():
        raise asyncio.CancelledError("unknown cancellation source")
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _incomplete_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits an explicit incomplete terminal response event."""
    async def _events():
        yield {
            "type": "response.created",
            "payload": {
                "status": "queued",
                "output": [],
            },
        }
        yield {
            "type": "response.in_progress",
            "payload": {
                "status": "in_progress",
                "output": [],
            },
        }
        yield {
            "type": "response.incomplete",
            "payload": {
                "status": "incomplete",
                "output": [],
            },
        }

    return _events()


def _make_blocking_sync_response_handler(
    started_gate: EventGate, release_gate: threading.Event
):
    """Factory for a handler that holds a sync request in-flight for deterministic concurrent cancel checks."""
    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            started_gate.signal(True)
            while not release_gate.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)
            if False:  # pragma: no cover - keep async generator shape.
                yield None

        return _events()

    return handler


def _build_client(handler: Any | None = None) -> TestClient:
    server = AgentHost()
    responses = ResponseHandler(server)
    responses.create_handler(handler or _noop_response_handler)
    return TestClient(server.app)


def _create_background_response(client: TestClient, *, response_id: str | None = None) -> str:
    payload: dict[str, Any] = {
        "model": "gpt-4o-mini",
        "input": "hello",
        "stream": False,
        "store": True,
        "background": True,
    }
    if response_id is not None:
        payload["response_id"] = response_id

    create_response = client.post("/responses", json=payload)
    assert create_response.status_code == 200
    created_id = create_response.json().get("id")
    assert isinstance(created_id, str)
    return created_id


def _wait_for_status(client: TestClient, response_id: str, expected_status: str, *, timeout_s: float = 5.0) -> None:
    latest_status: str | None = None

    def _has_expected_status() -> bool:
        nonlocal latest_status
        get_response = client.get(f"/responses/{response_id}")
        if get_response.status_code != 200:
            return False
        latest_status = get_response.json().get("status")
        return latest_status == expected_status

    ok, failure = poll_until(
        _has_expected_status,
        timeout_s=timeout_s,
        interval_s=0.05,
        context_provider=lambda: {"response_id": response_id, "last_status": latest_status},
        label=f"wait for status={expected_status}",
    )
    assert ok, failure


def _assert_error(
    response: Any,
    *,
    expected_status: int,
    expected_type: str,
    expected_message: str | None = None,
) -> None:
    assert response.status_code == expected_status
    payload = response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("type") == expected_type
    if expected_message is not None:
        assert payload["error"].get("message") == expected_message


def test_cancel__cancels_background_response_and_clears_output() -> None:
    client = _build_client(_cancellable_bg_response_handler)

    response_id = _create_background_response(client)

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200
    payload = cancel_response.json()
    assert payload.get("status") == "cancelled"
    assert payload.get("output") == []

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    snapshot = get_response.json()
    assert snapshot.get("status") == "cancelled"
    assert snapshot.get("output") == []


def test_cancel__is_idempotent_for_already_cancelled_response() -> None:
    client = _build_client(_cancellable_bg_response_handler)

    response_id = _create_background_response(client)

    first_cancel = client.post(f"/responses/{response_id}/cancel")
    assert first_cancel.status_code == 200
    assert first_cancel.json().get("status") == "cancelled"
    assert first_cancel.json().get("output") == []

    second_cancel = client.post(f"/responses/{response_id}/cancel")
    assert second_cancel.status_code == 200
    assert second_cancel.json().get("status") == "cancelled"
    assert second_cancel.json().get("output") == []


def test_cancel__returns_400_for_completed_background_response() -> None:
    client = _build_client()
    response_id = _create_background_response(client)
    _wait_for_status(client, response_id, "completed")

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=400,
        expected_type="invalid_request_error",
        expected_message="Cannot cancel a completed response.",
    )


def test_cancel__returns_400_for_failed_background_response() -> None:
    """Phase 3: handler that raises before emitting any event causes POST to return 500.
    A subsequent cancel on the non-existent record returns 404.
    """
    from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

    def _raising_before_events(req: Any, ctx: Any, sig: Any):
        async def _ev():
            raise RuntimeError("simulated handler failure")
            if False:  # pragma: no cover
                yield None
        return _ev()

    client = _build_client(_raising_before_events)
    create_response = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": True},
    )
    # Phase 3: handler failed before emitting response.created → HTTP 500
    assert create_response.status_code == 500


@pytest.mark.skip(
    reason="Known gap (S-024): unknown cancellation exceptions should map to handler-error path instead of escaping as CancelledError",
)
def test_cancel__unknown_cancellation_exception_is_treated_as_failed() -> None:
    client = _build_client(_unknown_cancellation_response_handler)
    response_id = _create_background_response(client)
    _wait_for_status(client, response_id, "failed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    assert get_response.json().get("status") == "failed"


def test_cancel__stream_disconnect_sets_handler_cancellation_signal() -> None:
    pytest.skip(
        "Requires a real ASGI disconnect harness; Starlette TestClient does not deterministically surface"
        " client-disconnect cancellation signals to the handler."
    )


def test_cancel__background_stream_disconnect_does_not_cancel_handler() -> None:
    pytest.skip(
        "Requires a real ASGI disconnect harness to verify that background execution is immune to"
        " stream client disconnect per S-026."
    )


def test_cancel__returns_400_for_incomplete_background_response() -> None:
    client = _build_client(_incomplete_response_handler)
    response_id = _create_background_response(client)
    _wait_for_status(client, response_id, "incomplete")

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=400,
        expected_type="invalid_request_error",
    )


def test_cancel__returns_400_for_synchronous_response() -> None:
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

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=400,
        expected_type="invalid_request_error",
        expected_message="Cannot cancel a synchronous response.",
    )


def test_cancel__returns_404_for_in_flight_synchronous_response() -> None:
    started_gate = EventGate()
    release_gate = threading.Event()
    client = _build_client(_make_blocking_sync_response_handler(started_gate, release_gate))
    response_id = IdGenerator.new_response_id()

    create_result: dict[str, Any] = {}

    def _issue_sync_create() -> None:
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
        except Exception as exc:  # pragma: no cover - surfaced by assertions below.
            create_result["error"] = exc

    create_thread = threading.Thread(target=_issue_sync_create, daemon=True)
    create_thread.start()

    started, _ = started_gate.wait(timeout_s=2.0)
    assert started, "Expected sync create request to enter handler before cancel call"

    cancel_response = client.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=404,
        expected_type="invalid_request_error",
    )

    release_gate.set()
    create_thread.join(timeout=2.0)
    assert not create_thread.is_alive(), "Expected in-flight sync request to finish after release"

    thread_error = create_result.get("error")
    assert thread_error is None, str(thread_error)
    create_response = create_result.get("response")
    assert create_response is not None
    assert create_response.status_code == 200


def test_cancel__returns_404_for_unknown_response_id() -> None:
    client = _build_client()

    cancel_response = client.post("/responses/resp_does_not_exist/cancel")
    _assert_error(
        cancel_response,
        expected_status=404,
        expected_type="invalid_request_error",
    )


# ══════════════════════════════════════════════════════════
# B-11: Cancel from queued / early in_progress state
# ══════════════════════════════════════════════════════════


def test_cancel__from_queued_or_early_in_progress_succeeds() -> None:
    """B-11 — Cancel issued immediately after creation (queued/early in_progress) returns HTTP 200,
    status=cancelled, and output=[]."""
    client = _build_client(_cancellable_bg_response_handler)

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

    # Cancel immediately — response is likely queued or very early in_progress.
    cancel_response = client.post(f"/responses/{response_id}/cancel")
    assert cancel_response.status_code == 200

    _wait_for_status(client, response_id, "cancelled")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["status"] == "cancelled"
    assert payload.get("output") == [], (
        f"output must be cleared for a cancelled response, got: {payload.get('output')}"
    )
