# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the structured close-event log line emitted by ``/invocations_ws``.

Parity with :mod:`tests.test_request_id` — verifies the spec's required
fields (``ws.session_id``, ``ws.close_code``, ``ws.duration_ms``) appear
on every connection close, and that handler exception details are NOT
leaked into the structured payload.
"""
import logging

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from azure.ai.agentserver.invocations._constants import InvocationsWSConstants

from conftest import (
    _make_echo_ws_app,
    _make_failing_ws_app,
    _records_with_ws_extras,
)


# ---------------------------------------------------------------------------
# Required fields on every close-event
# ---------------------------------------------------------------------------

def test_ws_close_event_log_contains_required_fields(caplog):
    """The close-event log line carries ws.session_id, ws.close_code, ws.duration_ms."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            assert ws.receive_text() == "ping"

    matches = _records_with_ws_extras(caplog.records)
    assert matches, "expected a structured close-event log record"
    rec = matches[-1]

    session_id = getattr(rec, "ws.session_id")
    close_code = getattr(rec, "ws.close_code")
    duration_ms = getattr(rec, "ws.duration_ms")

    assert isinstance(session_id, str) and session_id  # generated UUID
    assert close_code == InvocationsWSConstants.CLOSE_NORMAL
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


def test_ws_close_event_duration_is_non_negative(caplog):
    """``ws.duration_ms`` is a non-negative integer derived from a monotonic clock."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    duration_ms = getattr(matches[-1], "ws.duration_ms")
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


# ---------------------------------------------------------------------------
# Close codes on the close-event
# ---------------------------------------------------------------------------

def test_ws_close_event_on_handler_exception_records_1011(caplog):
    """Handler raising → close-event log records ws.close_code = 1011."""
    app = _make_failing_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("trigger")
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == 1011


# ---------------------------------------------------------------------------
# Exception details are NOT leaked into the structured payload
# (parity with test_error_hides_details_by_default)
# ---------------------------------------------------------------------------

def test_ws_close_event_log_does_not_leak_exception_message(caplog):
    """The close-event log line does NOT carry the handler exception text."""
    app = _make_failing_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("trigger")
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    rec = matches[-1]
    # The structured close-event log line carries only the safe ws.* fields.
    assert not hasattr(rec, "ws.error_message")
    # And the message itself does not embed the raw exception text.
    assert "boom" not in rec.getMessage()
