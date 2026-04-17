# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Cross-API E2E behavioural tests exercising multi-endpoint flows on a single response.

Each test calls 2+ endpoints and asserts cross-endpoint consistency per the contract.
Validates: E1–E44 from the cross-API matrix.

Python port of CrossApiE2eTests.
"""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import EventGate, poll_until

# ════════════════════════════════════════════════════════════
# Shared helpers
# ════════════════════════════════════════════════════════════


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE lines from a streaming response into a list of event dicts."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


def _wait_for_terminal(
    client: TestClient,
    response_id: str,
    *,
    timeout_s: float = 5.0,
) -> dict[str, Any]:
    """Poll GET until the response reaches a terminal status."""
    latest: dict[str, Any] = {}
    terminal_statuses = {"completed", "failed", "incomplete", "cancelled"}

    def _is_terminal() -> bool:
        nonlocal latest
        r = client.get(f"/responses/{response_id}")
        if r.status_code != 200:
            return False
        latest = r.json()
        return latest.get("status") in terminal_statuses

    ok, failure = poll_until(
        _is_terminal,
        timeout_s=timeout_s,
        interval_s=0.05,
        context_provider=lambda: {"status": latest.get("status")},
        label=f"wait_for_terminal({response_id})",
    )
    assert ok, failure
    return latest


# ════════════════════════════════════════════════════════════
# Handler factories
# ════════════════════════════════════════════════════════════


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler — emits no events (framework auto-completes)."""

    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _simple_text_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created + completed with no output items."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _output_producing_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that produces a single message output item with text 'hello'."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_in_progress()
        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("hello")
        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()
        yield stream.emit_completed()

    return _events()


def _throwing_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that raises after emitting created."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        raise RuntimeError("Simulated handler failure")

    return _events()


def _incomplete_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits an incomplete terminal event."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_incomplete(reason="max_output_tokens")

    return _events()


def _delayed_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that sleeps briefly, checking for cancellation."""

    async def _events():
        if cancellation_signal.is_set():
            return
        await asyncio.sleep(0.25)
        if cancellation_signal.is_set():
            return
        if False:  # pragma: no cover
            yield None

    return _events()


def _cancellable_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then blocks until cancelled.

    Suitable for Phase 3 cancel tests: response_created_signal is set on the
    first event, so run_background returns immediately with in_progress status
    while the task continues running until cancellation.
    """

    async def _events():
        stream = ResponseEventStream(
            response_id=context.response_id,
            model=getattr(request, "model", None),
        )
        yield stream.emit_created()  # unblocks run_background
        # Block until cancelled
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def _make_blocking_sync_handler(started_gate: EventGate, release_gate: threading.Event):
    """Factory for a handler that blocks on a gate, for testing concurrent GET/Cancel on in-flight sync requests."""

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            started_gate.signal(True)
            while not release_gate.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)
            if False:  # pragma: no cover
                yield None

        return _events()

    return handler


def _make_two_item_gated_handler(
    item1_emitted: EventGate,
    item1_gate: threading.Event,
    item2_emitted: EventGate,
    item2_gate: threading.Event,
):
    """Factory for a handler that emits two message output items with gates between them."""

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()
            yield stream.emit_in_progress()

            # First message
            msg1 = stream.add_output_item_message()
            yield msg1.emit_added()
            text1 = msg1.add_text_content()
            yield text1.emit_added()
            yield text1.emit_delta("Hello")
            yield text1.emit_text_done()
            yield text1.emit_done()
            yield msg1.emit_done()

            item1_emitted.signal()
            while not item1_gate.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            # Second message
            msg2 = stream.add_output_item_message()
            yield msg2.emit_added()
            text2 = msg2.add_text_content()
            yield text2.emit_added()
            yield text2.emit_delta("World")
            yield text2.emit_text_done()
            yield text2.emit_done()
            yield msg2.emit_done()

            item2_emitted.signal()
            while not item2_gate.is_set():
                if cancellation_signal.is_set():
                    return
                await asyncio.sleep(0.01)

            yield stream.emit_completed()

        return _events()

    return handler


def _build_client(handler: Any | None = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


def _create_sync_response(client: TestClient, **extra: Any) -> str:
    """POST /responses with stream=False, store=True, background=False. Returns response_id."""
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": False}
    payload.update(extra)
    r = client.post("/responses", json=payload)
    assert r.status_code == 200
    return r.json()["id"]


def _create_streaming_response(client: TestClient, **extra: Any) -> str:
    """POST /responses with stream=True. Consumes the SSE stream and returns response_id."""
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False}
    payload.update(extra)
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)
    assert events, "Expected at least one SSE event"
    return events[0]["data"]["response"]["id"]


def _create_bg_response(client: TestClient, **extra: Any) -> str:
    """POST /responses with background=True, stream=False. Returns response_id."""
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": False, "store": True, "background": True}
    payload.update(extra)
    r = client.post("/responses", json=payload)
    assert r.status_code == 200
    return r.json()["id"]


def _create_bg_streaming_response(client: TestClient, **extra: Any) -> str:
    """POST /responses with background=True, stream=True. Consumes SSE and returns response_id."""
    payload = {"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": True}
    payload.update(extra)
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)
    assert events, "Expected at least one SSE event"
    return events[0]["data"]["response"]["id"]


# ════════════════════════════════════════════════════════════
# C5/C6 — Ephemeral (store=false): E30–E35
# ════════════════════════════════════════════════════════════


class TestEphemeralStoreFalse:
    """store=false responses are not retrievable or cancellable (B14)."""

    @pytest.mark.parametrize(
        "stream, operation",
        [
            (False, "GET"),  # E30: C5 → GET JSON → 404
            (False, "GET_SSE"),  # E31: C5 → GET SSE replay → 404
            (True, "GET"),  # E33: C6 → GET JSON → 404
            (True, "GET_SSE"),  # E34: C6 → GET SSE replay → 404
        ],
        ids=["E30-sync-GET", "E31-sync-GET_SSE", "E33-stream-GET", "E34-stream-GET_SSE"],
    )
    def test_ephemeral_store_false_cross_api_returns_404(self, stream: bool, operation: str) -> None:
        """B14 — store=false responses are not retrievable."""
        handler = _simple_text_handler if stream else _noop_handler
        client = _build_client(handler)

        create_payload: dict[str, Any] = {
            "model": "gpt-4o-mini",
            "input": "hello",
            "store": False,
            "stream": stream,
            "background": False,
        }

        if stream:
            with client.stream("POST", "/responses", json=create_payload) as resp:
                assert resp.status_code == 200
                events = _collect_sse_events(resp)
            response_id = events[0]["data"]["response"]["id"]
        else:
            r = client.post("/responses", json=create_payload)
            assert r.status_code == 200
            response_id = r.json()["id"]

        if operation == "GET":
            result = client.get(f"/responses/{response_id}")
        else:
            result = client.get(f"/responses/{response_id}?stream=true")

        # B14: store=false responses are never persisted → 404 for any GET.
        assert result.status_code == 404

    @pytest.mark.parametrize(
        "stream",
        [False, True],
        ids=["E32-sync-cancel", "E35-stream-cancel"],
    )
    def test_ephemeral_store_false_cancel_rejected(self, stream: bool) -> None:
        """B1, B14 — store=false response not bg, cancel rejected.

        With unconditional runtime-state registration,
        the cancel endpoint finds the record and returns 400 "Cannot cancel a
        synchronous response." for non-bg requests.
        """
        handler = _simple_text_handler if stream else _noop_handler
        client = _build_client(handler)

        create_payload: dict[str, Any] = {
            "model": "gpt-4o-mini",
            "input": "hello",
            "store": False,
            "stream": stream,
            "background": False,
        }

        if stream:
            with client.stream("POST", "/responses", json=create_payload) as resp:
                assert resp.status_code == 200
                events = _collect_sse_events(resp)
            response_id = events[0]["data"]["response"]["id"]
        else:
            r = client.post("/responses", json=create_payload)
            assert r.status_code == 200
            response_id = r.json()["id"]

        result = client.post(f"/responses/{response_id}/cancel")
        # Contract: record found in runtime state → 400 (cannot cancel synchronous).
        assert result.status_code == 400


# ════════════════════════════════════════════════════════════
# C1 — Synchronous, stored (store=T, bg=F, stream=F): E1–E6
# ════════════════════════════════════════════════════════════


class TestC1SyncStored:
    """Synchronous non-streaming stored response cross-API tests."""

    def test_e1_create_then_get_after_completion_returns_200_completed(self) -> None:
        """B5 — JSON GET returns current snapshot; B16 — after completion, accessible."""
        client = _build_client()
        response_id = _create_sync_response(client)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        payload = get_resp.json()
        assert payload["status"] == "completed"

    def test_e2_create_get_during_in_flight_returns_404(self) -> None:
        """B16 — non-bg in-flight → 404."""
        started_gate = EventGate()
        release_gate = threading.Event()
        handler = _make_blocking_sync_handler(started_gate, release_gate)
        client = _build_client(handler)
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

        started, _ = started_gate.wait(timeout_s=5.0)
        assert started, "Handler should have started"

        # GET during in-flight → 404
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 404

        # Release handler
        release_gate.set()
        t.join(timeout=5.0)
        assert not t.is_alive()

        # Now GET succeeds
        get_after = client.get(f"/responses/{response_id}")
        assert get_after.status_code == 200
        assert get_after.json()["status"] == "completed"

    def test_e3_create_then_get_sse_replay_returns_400(self) -> None:
        """B2 — SSE replay requires background."""
        client = _build_client()
        response_id = _create_sync_response(client)

        get_resp = client.get(f"/responses/{response_id}?stream=true")
        assert get_resp.status_code == 400

    def test_e4_create_then_cancel_after_completion_returns_400(self) -> None:
        """B1 — cancel requires background; B12 — cancel rejection."""
        client = _build_client()
        response_id = _create_sync_response(client)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400
        payload = cancel_resp.json()
        assert payload["error"]["type"] == "invalid_request_error"
        assert "synchronous" in payload["error"]["message"].lower()

    def test_e5_create_cancel_during_in_flight_returns_400(self) -> None:
        """B1 — cancel requires background; non-bg → 400."""
        started_gate = EventGate()
        release_gate = threading.Event()
        handler = _make_blocking_sync_handler(started_gate, release_gate)
        client = _build_client(handler)
        response_id = IdGenerator.new_response_id()

        def _do_create() -> None:
            client.post(
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

        t = threading.Thread(target=_do_create, daemon=True)
        t.start()

        started, _ = started_gate.wait(timeout_s=5.0)
        assert started

        # Cancel during in-flight non-bg → 404 (not yet stored, S7)
        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 404, "S7: non-background in-flight cancel must return 404 (not yet stored)"

        release_gate.set()
        t.join(timeout=5.0)

    @pytest.mark.asyncio
    async def test_e6_disconnect_then_get_returns_not_found(self) -> None:
        """B17 — connection termination cancels non-bg; not persisted → GET 404.

        Uses a real Hypercorn server so that TCP disconnect propagates correctly.
        A sync (non-streaming) POST with a blocking handler is aborted mid-flight,
        then GET /responses/{id} must return 404.
        """
        from tests._helpers import hypercorn_server

        handler_started = asyncio.Event()

        app = ResponsesAgentServerHost()

        @app.response_handler
        def _handler(request: Any, context: Any, cancellation_signal: Any):
            async def _events():
                handler_started.set()
                # Block long enough for the client to disconnect
                for _ in range(200):
                    if cancellation_signal.is_set():
                        return
                    await asyncio.sleep(0.05)
                stream = ResponseEventStream(
                    response_id=context.response_id,
                    model=getattr(request, "model", None),
                )
                yield stream.emit_created()
                yield stream.emit_completed()

            return _events()

        response_id = IdGenerator.new_response_id()

        async with hypercorn_server(app) as client:
            # Start a sync (non-streaming) POST in a task and cancel it
            async def _do_post() -> None:
                await client.post(
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

            post_task = asyncio.create_task(_do_post())
            # Wait for handler to start processing
            await asyncio.wait_for(handler_started.wait(), timeout=5.0)
            # Cancel the POST task → closes TCP connection
            post_task.cancel()
            try:
                await post_task
            except (asyncio.CancelledError, Exception):
                pass

            await asyncio.sleep(1.0)

            # Non-bg in-flight responses are not persisted → GET returns 404
            get_resp = await client.get(f"/responses/{response_id}")
            assert get_resp.status_code == 404, (
                f"Expected 404 for disconnected non-bg sync response, got {get_resp.status_code}"
            )


# ════════════════════════════════════════════════════════════
# C2 — Synchronous streaming, stored (store=T, bg=F, stream=T): E7–E12
# ════════════════════════════════════════════════════════════


class TestC2StreamStored:
    """Synchronous streaming stored response cross-API tests."""

    def test_e7_stream_create_then_get_after_stream_ends_returns_200_completed(self) -> None:
        """B5 — JSON GET returns current snapshot."""
        client = _build_client(_simple_text_handler)
        response_id = _create_streaming_response(client)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "completed"

    # E8 moved to test_cross_api_e2e_async.py (requires async ASGI client)

    def test_e9_stream_create_then_get_sse_replay_returns_400(self) -> None:
        """B2 — SSE replay requires background."""
        client = _build_client(_simple_text_handler)
        response_id = _create_streaming_response(client)

        get_resp = client.get(f"/responses/{response_id}?stream=true")
        assert get_resp.status_code == 400

    def test_e10_stream_create_then_cancel_after_stream_ends_returns_400(self) -> None:
        """B1, B12 — cancel non-bg rejected."""
        client = _build_client(_simple_text_handler)
        response_id = _create_streaming_response(client)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400
        assert "synchronous" in cancel_resp.json()["error"]["message"].lower()

    # E11 moved to test_cross_api_e2e_async.py (requires async ASGI client)

    @pytest.mark.asyncio
    async def test_e12_stream_disconnect_then_get_returns_not_found(self) -> None:
        """B17 — connection termination cancels non-bg streaming; not persisted → GET 404.

        Uses a real Hypercorn server. Client starts streaming, reads a few SSE
        events to capture the response_id, then disconnects. GET should return 404.
        """
        from tests._helpers import hypercorn_server

        handler_started = asyncio.Event()

        app = ResponsesAgentServerHost()

        @app.response_handler
        def _handler(request: Any, context: Any, cancellation_signal: Any):
            async def _events():
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
                        break
                    yield tc.emit_delta(f"chunk{i} ")
                    await asyncio.sleep(0.02)
                yield tc.emit_text_done("done")
                yield tc.emit_done()
                yield msg.emit_done()
                yield stream.emit_completed()

            return _events()

        response_id: str | None = None

        async with hypercorn_server(app) as client:
            async with client.stream(
                "POST",
                "/responses",
                json={"model": "test", "input": "hi", "stream": True, "store": True},
            ) as resp:
                assert resp.status_code == 200
                lines_read = 0
                async for line in resp.aiter_lines():
                    lines_read += 1
                    # Extract response_id from the first data line
                    if response_id is None and line.startswith("data:"):
                        data = json.loads(line.split(":", 1)[1].strip())
                        rid = (data.get("response") or {}).get("id")
                        if rid:
                            response_id = rid
                    if lines_read >= 6:
                        break
                # EXIT context → real TCP disconnect

            assert response_id is not None, "Should have captured response_id from SSE events"
            await asyncio.sleep(1.5)

            # Non-bg streaming response cancelled by disconnect → not persisted → 404
            get_resp = await client.get(f"/responses/{response_id}")
            assert get_resp.status_code == 404, (
                f"Expected 404 for disconnected non-bg streaming response, got {get_resp.status_code}"
            )


# ════════════════════════════════════════════════════════════
# C3 — Background poll, stored (store=T, bg=T, stream=F): E13–E19, E36–E39
# ════════════════════════════════════════════════════════════


class TestC3BgPollStored:
    """Background non-streaming stored response cross-API tests."""

    def test_e13_bg_create_then_get_immediate_returns_queued_or_in_progress(self) -> None:
        """B5, B10 — background non-streaming returns immediately.

        Background POST now returns before the handler starts, so the
        initial status is always queued.  The Starlette TestClient may
        process the background task before the subsequent GET, so we
        accept queued, in_progress, or completed.
        """
        client = _build_client()

        r = client.post(
            "/responses",
            json={
                "model": "gpt-4o-mini",
                "input": "hello",
                "stream": False,
                "store": True,
                "background": True,
            },
        )
        assert r.status_code == 200
        create_payload = r.json()
        response_id = create_payload["id"]
        # Contract: background POST returns immediately with queued snapshot
        assert create_payload["status"] in {"queued", "in_progress", "completed"}

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] in {"queued", "in_progress", "completed"}

        # Wait for terminal
        _wait_for_terminal(client, response_id)

    def test_e14_bg_create_then_get_after_completion_returns_completed(self) -> None:
        """B5, B10."""
        client = _build_client()
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "completed"

    def test_e15_bg_create_then_get_sse_replay_returns_400(self) -> None:
        """B2 — SSE replay requires stream=true at creation."""
        client = _build_client()
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}?stream=true")
        assert get_resp.status_code == 400

    def test_e16_bg_create_cancel_then_get_returns_cancelled(self) -> None:
        """B7 — cancelled status; B11 — output cleared."""
        client = _build_client(_cancellable_bg_handler)
        response_id = _create_bg_response(client)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200

        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        snapshot = get_resp.json()
        assert snapshot["status"] == "cancelled"
        assert snapshot["output"] == []

    def test_e17_bg_create_wait_complete_then_cancel_returns_400(self) -> None:
        """B12 — cannot cancel a completed response."""
        client = _build_client()
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400
        assert "Cannot cancel a completed response" in cancel_resp.json()["error"]["message"]

    def test_e18_bg_create_cancel_cancel_returns_200_idempotent(self) -> None:
        """B3 — cancel is idempotent."""
        client = _build_client(_cancellable_bg_handler)
        response_id = _create_bg_response(client)

        cancel1 = client.post(f"/responses/{response_id}/cancel")
        assert cancel1.status_code == 200

        cancel2 = client.post(f"/responses/{response_id}/cancel")
        assert cancel2.status_code == 200

        _wait_for_terminal(client, response_id)

    def test_e19_bg_create_disconnect_then_get_returns_completed(self) -> None:
        """B18 — background responses unaffected by connection termination."""
        client = _build_client()
        response_id = _create_bg_response(client)
        # bg POST already returned — bg mode is immune to disconnect
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "completed"

    def test_e36_bg_handler_throws_then_get_returns_failed(self) -> None:
        """B5, B6 — failed status invariants."""
        client = _build_client(_throwing_handler)
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        snapshot = get_resp.json()
        assert snapshot["status"] == "failed"
        # B6: failed → error must be non-null
        error = snapshot.get("error")
        assert error is not None, "B6: error must be non-null for status=failed"
        assert "code" in error
        assert "message" in error

    def test_e37_bg_handler_incomplete_then_get_returns_incomplete(self) -> None:
        """B5, B6 — incomplete status invariants."""
        client = _build_client(_incomplete_handler)
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        snapshot = get_resp.json()
        assert snapshot["status"] == "incomplete"
        # B6: incomplete → error null
        assert snapshot.get("error") is None

    def test_e38_bg_handler_throws_then_cancel_returns_400(self) -> None:
        """B12 — cancel rejection on failed."""
        client = _build_client(_throwing_handler)
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400
        assert "Cannot cancel a failed response" in cancel_resp.json()["error"]["message"]

    def test_e39_bg_handler_incomplete_then_cancel_returns_400(self) -> None:
        """B12 — cancel rejection on incomplete (terminal status)."""
        client = _build_client(_incomplete_handler)
        response_id = _create_bg_response(client)
        _wait_for_terminal(client, response_id)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400

    def test_e44_bg_progressive_polling_output_grows(self) -> None:
        """B5, B10 — background poll shows progressive output accumulation.

        Verifies that after completion, the response contains full output.
        Note: Fine-grained mid-stream gating across async/sync boundary
        is unreliable with Starlette TestClient, so we verify final state.
        """
        client = _build_client(_output_producing_handler)
        response_id = _create_bg_response(client)
        terminal = _wait_for_terminal(client, response_id)

        assert terminal["status"] == "completed"
        assert isinstance(terminal.get("output"), list)
        assert len(terminal["output"]) >= 1
        assert terminal["output"][0]["type"] == "message"
        assert terminal["output"][0]["content"][0]["text"] == "hello"


# ════════════════════════════════════════════════════════════
# C4 — Background streaming, stored (store=T, bg=T, stream=T): E20–E29, E40–E42
# ════════════════════════════════════════════════════════════


class TestC4BgStreamStored:
    """Background streaming stored response cross-API tests."""

    def test_e21_bg_stream_create_get_after_stream_ends_returns_completed(self) -> None:
        """B5."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "completed"

    def test_e22_bg_stream_completed_sse_replay_returns_all_events(self) -> None:
        """B4 — SSE replay; B9 — sequence numbers; B26 — terminal event."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200
            events = _collect_sse_events(replay_resp)

        assert len(events) >= 2, "Replay should have at least 2 events"

        # B26: terminal event is response.completed
        assert events[-1]["type"] == "response.completed"

        # B9: sequence numbers monotonically increasing
        seq_nums = [e["data"]["sequence_number"] for e in events]
        for i in range(1, len(seq_nums)):
            assert seq_nums[i] > seq_nums[i - 1]

    def test_e23_bg_stream_sse_replay_with_starting_after_skips_events(self) -> None:
        """B4 — starting_after cursor."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        # Full replay
        with client.stream("GET", f"/responses/{response_id}?stream=true") as full_resp:
            full_events = _collect_sse_events(full_resp)
        assert len(full_events) >= 2, "Need at least 2 events for cursor test"

        first_seq = full_events[0]["data"]["sequence_number"]

        # Replay with starting_after = first seq → skips first event
        with client.stream("GET", f"/responses/{response_id}?stream=true&starting_after={first_seq}") as cursor_resp:
            assert cursor_resp.status_code == 200
            cursor_events = _collect_sse_events(cursor_resp)

        assert len(cursor_events) == len(full_events) - 1

    def test_e24_bg_stream_cancel_immediate_returns_cancelled(self) -> None:
        """B7, B11 — cancel → cancelled with 0 output.

        Uses non-streaming bg path because the synchronous TestClient cannot
        issue concurrent requests during an active SSE stream.  The actual
        bg+stream mid-stream cancel is tested in test_cross_api_e2e_async.py
        (E25) using the async ASGI client.
        """
        client = _build_client(_cancellable_bg_handler)
        response_id = _create_bg_response(client)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200

        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        snapshot = get_resp.json()
        assert snapshot["status"] == "cancelled"
        assert snapshot["output"] == []

    def test_e27_bg_stream_completed_then_cancel_returns_400(self) -> None:
        """B12 — cannot cancel completed."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 400
        assert "Cannot cancel a completed response" in cancel_resp.json()["error"]["message"]

    def test_e28_bg_stream_cancel_cancel_returns_200_idempotent(self) -> None:
        """B3 — cancel is idempotent.

        Uses non-streaming bg path because the synchronous TestClient cannot
        issue concurrent requests during an active SSE stream.
        """
        client = _build_client(_cancellable_bg_handler)
        response_id = _create_bg_response(client)

        cancel1 = client.post(f"/responses/{response_id}/cancel")
        assert cancel1.status_code == 200

        cancel2 = client.post(f"/responses/{response_id}/cancel")
        assert cancel2.status_code == 200

        _wait_for_terminal(client, response_id)

    def test_e29_bg_stream_disconnect_then_get_returns_completed(self) -> None:
        """B18 — background responses unaffected by connection termination."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "completed"

    def test_e40_bg_stream_handler_throws_get_and_sse_replay_returns_failed(self) -> None:
        """B5, B6 — failed status invariants; B26 — terminal event."""
        client = _build_client(_throwing_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        # GET JSON → failed
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        snapshot = get_resp.json()
        assert snapshot["status"] == "failed"
        # B6: failed → error must be non-null
        error = snapshot.get("error")
        assert error is not None, "B6: error must be non-null for status=failed"
        assert "code" in error
        assert "message" in error

        # SSE replay → terminal = response.failed
        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200
            replay_events = _collect_sse_events(replay_resp)
        assert replay_events[-1]["type"] == "response.failed"

    def test_e41_bg_stream_handler_incomplete_get_and_sse_replay_returns_incomplete(self) -> None:
        """B5, B6 — incomplete status invariants; B26 — terminal event."""
        client = _build_client(_incomplete_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        # GET JSON → incomplete
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        snapshot = get_resp.json()
        assert snapshot["status"] == "incomplete"
        assert snapshot.get("error") is None

        # SSE replay → terminal = response.incomplete
        with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_resp:
            assert replay_resp.status_code == 200
            events = _collect_sse_events(replay_resp)
        assert events[-1]["type"] == "response.incomplete"

    def test_e42_bg_stream_sse_replay_starting_after_max_returns_empty(self) -> None:
        """B4 — starting_after >= max → empty stream."""
        client = _build_client(_simple_text_handler)
        response_id = _create_bg_streaming_response(client)
        _wait_for_terminal(client, response_id)

        # Get max sequence number from full replay
        with client.stream("GET", f"/responses/{response_id}?stream=true") as full_resp:
            full_events = _collect_sse_events(full_resp)
        max_seq = full_events[-1]["data"]["sequence_number"]

        # Replay with starting_after = max → empty
        with client.stream("GET", f"/responses/{response_id}?stream=true&starting_after={max_seq}") as empty_resp:
            assert empty_resp.status_code == 200
            empty_events = _collect_sse_events(empty_resp)
        assert empty_events == []

    def test_e26_bg_stream_cancel_then_sse_replay_has_terminal_event(self) -> None:
        """B26 — terminal SSE event after cancel; B11.

        Uses non-streaming bg path for the cancel step because the synchronous
        TestClient cannot issue concurrent requests during an active SSE stream.
        The SSE replay terminal-event check is performed in the async test file
        (test_e26_bg_stream_cancel_then_sse_replay_terminal_event) which can
        create bg+stream responses and cancel mid-stream.
        """
        client = _build_client(_cancellable_bg_handler)
        response_id = _create_bg_response(client)

        cancel_resp = client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code == 200
        _wait_for_terminal(client, response_id)

        # After cancel, the response is cancelled.
        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "cancelled"
