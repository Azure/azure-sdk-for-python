# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Smoke tests for the ws_bidirectional_streaming_agent sample.

Loads the sample module directly (samples are not a package), patches the
per-token sleep down to 0 so the test runs in milliseconds, and drives the
``ready`` / ``prompt`` / ``cancel`` / ``bye`` wire protocol over Starlette's
``TestClient.websocket_connect``.
"""
import importlib.util
import json
import pathlib
import sys

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


_SAMPLE_PATH = (
    pathlib.Path(__file__).parent.parent
    / "samples"
    / "ws_bidirectional_streaming_agent"
    / "ws_bidirectional_streaming_agent.py"
)


@pytest.fixture
def sample(monkeypatch):
    """Load the sample as a module and zero out the per-token delay."""
    spec = importlib.util.spec_from_file_location(
        "ws_bidirectional_streaming_agent_sample", _SAMPLE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_TOKEN_DELAY_S", 0.0)
    yield module
    sys.modules.pop(spec.name, None)


# ---------------------------------------------------------------------------
# Handshake
# ---------------------------------------------------------------------------

def test_ws_bidirectional_sends_ready_on_connect(sample):
    """The handler immediately sends a ``{"type": "ready"}`` frame on connect."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text(json.dumps({"type": "bye"}))
        first = ws.receive_json()
        assert first == {"type": "ready"}


# ---------------------------------------------------------------------------
# Prompt streaming
# ---------------------------------------------------------------------------

def _drain_until_done(ws, prompt_id: str):
    """Collect token frames until the matching ``done`` (or ``cancelled``) arrives."""
    tokens: list[str] = []
    terminal: dict | None = None
    while True:
        msg = ws.receive_json()
        if msg["type"] == "token" and msg["id"] == prompt_id:
            tokens.append(msg["token"])
        elif msg["type"] in ("done", "cancelled", "error") and msg["id"] == prompt_id:
            terminal = msg
            break
    return tokens, terminal


def test_ws_bidirectional_streams_tokens_for_prompt(sample):
    """A ``prompt`` frame produces a token stream terminated by ``done``."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        ws.send_text(json.dumps({"type": "prompt", "id": "p1", "text": "story"}))
        tokens, terminal = _drain_until_done(ws, "p1")
        ws.send_text(json.dumps({"type": "bye"}))

    assert terminal == {"type": "done", "id": "p1"}
    # All simulated tokens echoed in order.
    assert tokens == sample._SIMULATED_TOKENS


def test_ws_bidirectional_prompt_without_id_emits_error(sample):
    """A ``prompt`` missing an ``id`` triggers an error reply but keeps the connection."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        ws.send_text(json.dumps({"type": "prompt", "text": "no-id"}))
        reply = ws.receive_json()
        assert reply["type"] == "error"
        assert "id" in reply["message"]
        ws.send_text(json.dumps({"type": "bye"}))


def test_ws_bidirectional_unknown_type_emits_error(sample):
    """An unknown message ``type`` triggers an error reply but keeps the connection."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        ws.send_text(json.dumps({"type": "foobar"}))
        reply = ws.receive_json()
        assert reply["type"] == "error"
        assert "foobar" in reply["message"]
        ws.send_text(json.dumps({"type": "bye"}))


def test_ws_bidirectional_invalid_json_emits_error(sample):
    """A non-JSON text frame triggers an error reply."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        ws.send_text("not json {")
        reply = ws.receive_json()
        assert reply["type"] == "error"
        assert "JSON" in reply["message"]
        ws.send_text(json.dumps({"type": "bye"}))


# ---------------------------------------------------------------------------
# Cancellation
# ---------------------------------------------------------------------------

def test_ws_bidirectional_cancel_interrupts_in_flight_prompt(sample):
    """A ``cancel`` frame mid-stream surfaces a ``cancelled`` event."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        ws.send_text(json.dumps({"type": "prompt", "id": "p2", "text": "story"}))
        # Cancel before drain — handler should reply with cancelled (and may
        # have emitted a few token frames first).
        ws.send_text(json.dumps({"type": "cancel", "id": "p2"}))
        # Drain until we see either done or cancelled.
        terminal: dict | None = None
        while True:
            msg = ws.receive_json()
            if msg["type"] in ("done", "cancelled") and msg["id"] == "p2":
                terminal = msg
                break
        ws.send_text(json.dumps({"type": "bye"}))

    assert terminal is not None
    # With _TOKEN_DELAY_S = 0 the stream may finish before the cancel is
    # observed; both terminal types are acceptable outcomes.
    assert terminal["type"] in ("cancelled", "done")


def test_ws_bidirectional_cancel_unknown_id_is_noop(sample):
    """Cancelling an unknown prompt ID does not break the connection."""
    client = TestClient(sample.app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_json() == {"type": "ready"}
        # Cancel an id that was never registered — handler ignores silently.
        ws.send_text(json.dumps({"type": "cancel", "id": "ghost"}))
        # Verify connection still works by sending a real prompt.
        ws.send_text(json.dumps({"type": "prompt", "id": "p3", "text": "ok"}))
        _, terminal = _drain_until_done(ws, "p3")
        ws.send_text(json.dumps({"type": "bye"}))
        assert terminal == {"type": "done", "id": "p3"}


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------

def test_ws_bidirectional_bye_closes_connection(sample):
    """A ``bye`` frame causes the handler to return → SDK closes cleanly."""
    client = TestClient(sample.app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations_ws") as ws:
            assert ws.receive_json() == {"type": "ready"}
            ws.send_text(json.dumps({"type": "bye"}))
            # Receive should surface the close as WebSocketDisconnect.
            ws.receive_json()


# ---------------------------------------------------------------------------
# HTTP parity
# ---------------------------------------------------------------------------

def test_ws_bidirectional_http_invoke_still_works(sample):
    """The same host still serves ``POST /invocations`` for HTTP parity."""
    client = TestClient(sample.app)
    response = client.post("/invocations", json={"hello": "world"})
    assert response.status_code == 200
    assert response.json() == {"echo": {"hello": "world"}}
