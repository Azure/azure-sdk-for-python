# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for sentinel removal (US1, US2).

Validates that no SSE stream contains ``data: [DONE]`` under any scenario.
Validates: B26 — Terminal SSE events (no [DONE] sentinel).

Python port of SentinelRemovalProtocolTests.
"""

from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _simple_text_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits a complete text message output."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()
        text = msg.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("Hello")
        yield text.emit_text_done()
        yield text.emit_done()
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def _failing_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then raises an exception."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        raise RuntimeError("Simulated handler failure")

    return _events()


def _incomplete_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then response.incomplete."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_incomplete()

    return _events()


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:
            yield None

    return _events()


def _build_client(handler: Any) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return TestClient(app)


def _wait_for_terminal(client: TestClient, response_id: str) -> None:
    ok, diag = poll_until(
        lambda: (
            client.get(f"/responses/{response_id}").json().get("status")
            in ("completed", "failed", "incomplete", "cancelled")
        ),
        timeout_s=5.0,
        label="wait_for_terminal",
    )
    assert ok, diag


# ════════════════════════════════════════════════════════════
# US1: Live streams must not contain [DONE] sentinel
# ════════════════════════════════════════════════════════════


def test_live_stream_completed_no_done_sentinel() -> None:
    """Live SSE stream for completed response must not contain data: [DONE]."""
    client = _build_client(_simple_text_handler)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        lines = list(resp.iter_lines())
    body = "\n".join(lines)

    assert "data: [DONE]" not in body


def test_live_stream_failed_no_done_sentinel() -> None:
    """Live SSE stream for failed response must not contain data: [DONE]."""
    client = _build_client(_failing_handler)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        lines = list(resp.iter_lines())
    body = "\n".join(lines)

    assert "data: [DONE]" not in body
    # Verify the stream contains a response.failed terminal event
    assert "response.failed" in body


def test_live_stream_incomplete_no_done_sentinel() -> None:
    """Live SSE stream for incomplete response must not contain data: [DONE]."""
    client = _build_client(_incomplete_handler)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        lines = list(resp.iter_lines())
    body = "\n".join(lines)

    assert "data: [DONE]" not in body
    # Verify the stream contains a response.incomplete terminal event
    assert "response.incomplete" in body


# ════════════════════════════════════════════════════════════
# US2: Replay streams must not contain [DONE] sentinel
# ════════════════════════════════════════════════════════════


def test_replay_stream_completed_no_done_sentinel() -> None:
    """Replayed SSE stream for completed bg+stream response must not contain data: [DONE]."""
    from azure.ai.agentserver.responses._id_generator import IdGenerator

    client = _build_client(_simple_text_handler)
    response_id = IdGenerator.new_response_id()

    # Create a bg+stream response (required for SSE replay)
    with client.stream(
        "POST",
        "/responses",
        json={
            "response_id": response_id,
            "model": "test",
            "background": True,
            "stream": True,
            "store": True,
        },
    ) as resp:
        assert resp.status_code == 200
        # Consume SSE stream to completion
        list(resp.iter_lines())

    _wait_for_terminal(client, response_id)

    # GET SSE replay
    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
        assert replay.status_code == 200
        lines = list(replay.iter_lines())
    body = "\n".join(lines)

    assert "data: [DONE]" not in body
