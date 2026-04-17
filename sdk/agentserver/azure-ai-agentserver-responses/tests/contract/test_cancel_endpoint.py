# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for POST /responses/{response_id}/cancel behavior."""

from __future__ import annotations

import asyncio
import threading
from typing import Any

import pytest
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
            "response": {
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
            "response": {
                "status": "queued",
                "output": [],
            },
        }
        yield {
            "type": "response.in_progress",
            "response": {
                "status": "in_progress",
                "output": [],
            },
        }
        yield {
            "type": "response.incomplete",
            "response": {
                "status": "incomplete",
                "output": [],
            },
        }

    return _events()


def _make_blocking_sync_response_handler(started_gate: EventGate, release_gate: threading.Event):
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
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_response_handler)
    return TestClient(app)


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


def test_cancel__returns_failed_for_immediate_handler_failure() -> None:
    """Background POST waits for response.created; when the handler fails
    before emitting it, the POST returns 200 with status=failed.
    """

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
    # Background POST returns 200 — failure reflected in status, not HTTP code
    assert create_response.status_code == 200
    payload = create_response.json()
    assert payload.get("status") == "failed"


def test_cancel__unknown_cancellation_exception_is_treated_as_failed() -> None:
    """S-024: An unknown CancelledError (not from cancel signal) should be
    treated as a handler error, transitioning the response to failed."""
    client = _build_client(_unknown_cancellation_response_handler)
    response_id = _create_background_response(client)
    _wait_for_status(client, response_id, "failed")

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    assert get_response.json().get("status") == "failed"


@pytest.mark.asyncio
async def test_cancel__stream_disconnect_sets_handler_cancellation_signal() -> None:
    """Non-bg streaming: client disconnect → handler generator cancelled.

    Uses a real Hypercorn server so that TCP disconnect propagates as
    asyncio.CancelledError to the streaming generator.
    """
    from tests._helpers import hypercorn_server

    handler_started = asyncio.Event()
    handler_cancelled = asyncio.Event()
    handler_completed = asyncio.Event()

    app = ResponsesAgentServerHost()

    @app.response_handler
    def _handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            handler_started.set()
            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()
            for i in range(500):
                if cancellation_signal.is_set():
                    handler_cancelled.set()
                    break
                yield tc.emit_delta(f"chunk{i} ")
                await asyncio.sleep(0.02)
            yield tc.emit_text_done("cancelled")
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_incomplete(reason="cancelled")
            handler_completed.set()

        return _events()

    async with hypercorn_server(app) as client:
        async with client.stream(
            "POST",
            "/responses",
            json={"model": "test", "input": "hi", "stream": True},
        ) as resp:
            assert resp.status_code == 200
            lines_read = 0
            async for _line in resp.aiter_lines():
                lines_read += 1
                if lines_read >= 5:
                    break
            # EXIT context → real TCP disconnect

        # Give server time to detect disconnect
        await asyncio.sleep(1.5)

        assert handler_started.is_set(), "Handler should have started"
        # The generator should have been cancelled by Hypercorn's
        # CancelledError propagation. The handler either saw cancellation_signal
        # or was killed by CancelledError before reaching the check.
        assert not handler_completed.is_set(), (
            "Handler should NOT have completed all 500 chunks — disconnect should stop it"
        )


@pytest.mark.asyncio
async def test_cancel__background_stream_disconnect_does_not_cancel_handler() -> None:
    """S-026: Background streaming disconnect does NOT cancel the handler.

    Uses a real Hypercorn server. Background execution is shielded from
    HTTP scope cancellation, so the handler runs to completion even after
    the streaming client disconnects.
    """
    from tests._helpers import hypercorn_server

    handler_started = asyncio.Event()
    handler_completed = asyncio.Event()

    app = ResponsesAgentServerHost()

    @app.response_handler
    def _handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            handler_started.set()
            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()
            # Emit a handful of chunks then complete normally
            for i in range(10):
                yield tc.emit_delta(f"chunk{i} ")
                await asyncio.sleep(0.05)
            yield tc.emit_text_done("done")
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_completed()
            handler_completed.set()

        return _events()

    async with hypercorn_server(app) as client:
        async with client.stream(
            "POST",
            "/responses",
            json={"model": "test", "input": "hi", "stream": True, "background": True},
        ) as resp:
            assert resp.status_code == 200
            lines_read = 0
            async for _line in resp.aiter_lines():
                lines_read += 1
                if lines_read >= 3:
                    break
            # EXIT context → real TCP disconnect

        # Wait for the background handler to complete
        await asyncio.wait_for(handler_completed.wait(), timeout=5.0)
        assert handler_started.is_set(), "Handler should have started"
        assert handler_completed.is_set(), "Background handler should complete normally despite client disconnect"


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
# B11: Cancel from queued / early in_progress state
# ══════════════════════════════════════════════════════════


def test_cancel__from_queued_or_early_in_progress_succeeds() -> None:
    """B11 — Cancel issued immediately after creation (queued/early in_progress) returns HTTP 200,
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
    assert payload.get("output") == [], f"output must be cleared for a cancelled response, got: {payload.get('output')}"


# ══════════════════════════════════════════════════════════
# B11 winddown: cancel timeout forces termination
# ══════════════════════════════════════════════════════════


def _stubborn_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that ignores the cancellation signal entirely."""

    async def _events():
        yield {
            "type": "response.created",
            "response": {
                "status": "in_progress",
                "output": [],
            },
        }
        # Block forever, ignoring the cancellation signal
        while True:
            await asyncio.sleep(0.01)

    return _events()


def test_cancel__winddown_forces_termination_when_handler_ignores_signal() -> None:
    """B11 winddown — if the handler ignores the cancellation signal, the
    background task still reaches a terminal state within the winddown timeout."""
    import azure.ai.agentserver.responses.hosting._orchestrator as _orch

    original = _orch._CANCEL_WINDDOWN_TIMEOUT
    _orch._CANCEL_WINDDOWN_TIMEOUT = 0.5  # shorten for test speed
    try:
        client = _build_client(_stubborn_handler)
        response_id = _create_background_response(client)

        cancel_response = client.post(f"/responses/{response_id}/cancel")
        assert cancel_response.status_code == 200

        # The background task should terminate within the winddown timeout
        _wait_for_status(client, response_id, "cancelled", timeout_s=5.0)
    finally:
        _orch._CANCEL_WINDDOWN_TIMEOUT = original


# ══════════════════════════════════════════════════════════
# B12: Cancel fallback for stored terminal responses after restart
# ══════════════════════════════════════════════════════════


def test_cancel__provider_fallback_returns_400_for_completed_after_restart() -> None:
    """B12 — cancel on a completed response whose runtime record was lost
    (simulated restart) returns 400 instead of 404."""
    from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

    provider = InMemoryResponseProvider()

    # First app instance: create and complete a response
    app1 = ResponsesAgentServerHost(store=provider)
    app1.response_handler(_noop_response_handler)
    client1 = TestClient(app1)
    response_id = _create_background_response(client1)
    _wait_for_status(client1, response_id, "completed")

    # Second app instance (simulating restart): fresh runtime state, same provider
    app2 = ResponsesAgentServerHost(store=provider)
    app2.response_handler(_noop_response_handler)
    client2 = TestClient(app2)

    cancel_response = client2.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=400,
        expected_type="invalid_request_error",
        expected_message="Cannot cancel a completed response.",
    )


def test_cancel__provider_fallback_returns_400_for_failed_after_restart() -> None:
    """B12 — cancel on a failed response whose runtime record was lost returns 400."""
    from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

    provider = InMemoryResponseProvider()

    # First app instance: create a response that fails
    app1 = ResponsesAgentServerHost(store=provider)
    app1.response_handler(_raising_response_handler)
    client1 = TestClient(app1)
    response_id = _create_background_response(client1)
    _wait_for_status(client1, response_id, "failed")

    # Second app instance (simulating restart)
    app2 = ResponsesAgentServerHost(store=provider)
    app2.response_handler(_noop_response_handler)
    client2 = TestClient(app2)

    cancel_response = client2.post(f"/responses/{response_id}/cancel")
    _assert_error(
        cancel_response,
        expected_status=400,
        expected_type="invalid_request_error",
        expected_message="Cannot cancel a failed response.",
    )


def test_cancel__persisted_state_is_cancelled_even_when_handler_completes_after_timeout() -> None:
    """B11 race condition: handler eventually yields response.completed after cancel.

    The durable store must still reflect 'cancelled', not 'completed'.
    """
    from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider

    provider = InMemoryResponseProvider()

    def _uncooperative_handler(request: Any, context: Any, cancellation_signal: Any):
        """Handler that ignores cancellation and eventually completes."""

        async def _events():
            yield {
                "type": "response.created",
                "response": {"status": "in_progress", "output": []},
            }
            # Deliberately ignores cancellation_signal — simulates uncooperative handler.
            # The short sleep ensures the handler is still "running" when cancel comes in,
            # but completes before the 10s winddown deadline.
            await asyncio.sleep(0.5)
            yield {
                "type": "response.completed",
                "response": {"status": "completed", "output": []},
            }

        return _events()

    app = ResponsesAgentServerHost(store=provider)
    app.response_handler(_uncooperative_handler)
    client = TestClient(app)

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": True, "background": True},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    # Cancel — the handler is still running
    cancel = client.post(f"/responses/{response_id}/cancel")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    # Wait for background task to fully finalize
    import time

    time.sleep(2.0)

    # GET from durable store must show cancelled
    get = client.get(f"/responses/{response_id}")
    assert get.status_code == 200
    assert get.json()["status"] == "cancelled", (
        "B11: Persisted state must be 'cancelled' — cancellation always wins, "
        "even when the handler yields response.completed after cancel"
    )


def test_cancel__in_progress_response_triggers_cancellation_signal() -> None:
    """Cancel triggers the cancellation_signal provided to the handler.

    Ported from CancelResponseProtocolTests.Cancel_InProgressResponse_TriggersCancellationToken.
    """

    def _tracking_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {
                "type": "response.created",
                "response": {"status": "in_progress", "output": []},
            }
            # Block until cancel; the asyncio.sleep yields to the event loop
            # so the cancel endpoint's signal actually propagates.
            for _ in range(500):
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

        return _events()

    client = _build_client(_tracking_handler)

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": True, "background": True},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    cancel = client.post(f"/responses/{response_id}/cancel")
    assert cancel.status_code == 200

    # If the signal was triggered the handler should have exited and the
    # response reached a terminal state ("cancelled").
    _wait_for_status(client, response_id, "cancelled", timeout_s=5.0)
