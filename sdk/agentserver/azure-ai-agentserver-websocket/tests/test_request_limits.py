# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for request processing (timeout feature removed per spec alignment)."""
import asyncio

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.conversations import (
    ConversationAgentServerHost,
    ConversationContext,
)


# ---------------------------------------------------------------------------
# ConversationAgentServerHost no longer accepts request_timeout
# ---------------------------------------------------------------------------

def test_no_request_timeout_parameter():
    """ConversationAgentServerHost no longer accepts request_timeout."""
    with pytest.raises(TypeError):
        ConversationAgentServerHost(request_timeout=10)


# ---------------------------------------------------------------------------
# Slow invoke completes without timeout
# ---------------------------------------------------------------------------

def test_slow_invoke_completes():
    """Without timeout, handler runs to completion."""
    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        await asyncio.sleep(0.1)
        return {"status": "done"}

    client = TestClient(app)
    with client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["status"] == "done"
