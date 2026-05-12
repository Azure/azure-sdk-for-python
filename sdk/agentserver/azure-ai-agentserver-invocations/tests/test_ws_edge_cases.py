# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Edge-case tests for ``/invocations_ws``.

Parity with :mod:`tests.test_edge_cases` — covers client-initiated
disconnects, handler-managed close, custom close codes, and empty
connections.
"""
import logging

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants

from conftest import _make_echo_ws_app, _records_with_ws_extras


# ---------------------------------------------------------------------------
# Client-initiated disconnect (clean)
# ---------------------------------------------------------------------------

def test_ws_client_disconnect_does_not_log_as_error(caplog):
    """A client-initiated disconnect is a normal close, not a 1011 error."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("hello")
            ws.receive_text()
            # __exit__ sends websocket.disconnect — the SDK should treat
            # this as normal, not raise from the handler.

    error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
    # No ERROR-level records should be emitted for a clean client disconnect.
    assert not error_records, [r.getMessage() for r in error_records]


# ---------------------------------------------------------------------------
# Client-initiated close with a custom (non-1000) code
# ---------------------------------------------------------------------------

def test_ws_client_initiated_close_with_custom_code_is_reported(caplog):
    """When the client closes with a non-1000 code, the server surfaces the client's code (not 1011)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        # Use receive_text directly so WebSocketDisconnect propagates with
        # the client's close code — ``iter_text`` swallows it.
        while True:
            await websocket.receive_text()

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("warm-up")
            ws.close(code=4001)

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    rec = matches[-1]
    close_code = getattr(rec, "ws.close_code")
    # Server surfaces the client's code — NOT 1011.
    assert close_code == 4001
    # No ERROR-level records — a client disconnect is normal.
    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]


# ---------------------------------------------------------------------------
# Handler-managed close
# ---------------------------------------------------------------------------

def test_ws_handler_explicit_close_does_not_double_close(caplog):
    """If the handler closes the WS itself, the SDK does NOT attempt a second close."""
    app = InvocationAgentServerHost()
    closes_observed: list[int] = []

    async def handler(websocket: WebSocket) -> None:
        # Hand-roll close so we can verify the SDK skips re-closing.
        await websocket.send_text("bye")
        await websocket.close(code=1000)
        closes_observed.append(1)

    app.ws_handler(handler)

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                assert ws.receive_text() == "bye"
                ws.receive_text()  # forces the close frame to surface

    # Handler ran to completion.
    assert closes_observed == [1]
    # Close-event log line still emitted (with the handler's code).
    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL


# ---------------------------------------------------------------------------
# Empty connection (no frames sent)
# ---------------------------------------------------------------------------

def test_ws_empty_connection_closes_normally(caplog):
    """A connection that immediately disconnects closes cleanly (1000)."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws"):
            pass  # Disconnect without sending anything.

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL
