# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for WebSocket session ID resolution.

Parity with :mod:`tests.test_session_id` — covers per-connection UUID
generation and the (deliberate) lack of query-param overrides.  The WS
endpoint always generates a fresh server-side session ID.
"""
import logging
import uuid

from starlette.testclient import TestClient

from conftest import _make_echo_ws_app, _records_with_ws_extras


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _session_ids_from_records(records):
    """Pull ``ws.session_id`` from each structured close-event record."""
    return [getattr(r, "ws.session_id") for r in _records_with_ws_extras(records)]


# ---------------------------------------------------------------------------
# Session ID is a server-generated UUID
# ---------------------------------------------------------------------------

def test_ws_session_id_is_uuid(caplog):
    """The per-connection session ID is a valid UUID string."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("hi")
            ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert session_ids
    # Each must parse as a UUID — the WS endpoint generates one server-side.
    parsed = uuid.UUID(session_ids[-1])
    assert str(parsed) == session_ids[-1]


def test_ws_session_id_is_unique_per_connection(caplog):
    """Each WS connection gets its own session ID (parity with test_invoke_unique_invocation_ids)."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        for _ in range(5):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("ping")
                ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert len(session_ids) == 5
    assert len(set(session_ids)) == 5


def test_ws_session_id_ignores_query_param(caplog):
    """Unlike HTTP, the WS endpoint always generates its own session ID."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect(
            "/invocations_ws?agent_session_id=my-custom-session",
        ) as ws:
            ws.send_text("x")
            ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert session_ids
    # The client's value MUST NOT leak into the session ID — the WS spec
    # generates a fresh server-side UUID per connection.
    assert session_ids[-1] != "my-custom-session"
    uuid.UUID(session_ids[-1])
