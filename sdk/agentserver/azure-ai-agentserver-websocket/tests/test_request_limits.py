# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for request processing (timeout feature removed per spec alignment)."""
import asyncio

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
)


# ---------------------------------------------------------------------------
# WebsocketAgentServerHost no longer accepts request_timeout
# ---------------------------------------------------------------------------

def test_no_request_timeout_parameter():
    """WebsocketAgentServerHost no longer accepts request_timeout."""
    with pytest.raises(TypeError):
        WebsocketAgentServerHost(request_timeout=10)


# ---------------------------------------------------------------------------
# Slow invoke completes without timeout
# ---------------------------------------------------------------------------

def test_slow_invoke_completes():
    """Without timeout, handler runs to completion."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        await asyncio.sleep(0.1)
        return {"status": "done"}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["status"] == "done"
