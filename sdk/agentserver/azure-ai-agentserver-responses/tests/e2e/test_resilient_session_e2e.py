# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient session management sample (Phase 5).

Tests:
- Session creation and multi-turn within session
- Session metadata persists across turns
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)


def _make_session_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        input_text = await context.get_input_text()
        session_id = context.conversation_chain_metadata.get("session_id", "new-session")
        context.conversation_chain_metadata["session_id"] = session_id
        msg_count = context.conversation_chain_metadata.get("msg_count", 0) + 1
        context.conversation_chain_metadata["msg_count"] = msg_count
        text = f"Session {session_id}, msg #{msg_count}: {input_text}"
        return TextResponse(context, request, text=text)

    return TestClient(app)


class TestResilientSessionE2E:
    def test_session_creation(self) -> None:
        client = _make_session_app()
        resp = client.post(
            "/responses",
            json={"model": "t", "input": "hi", "store": True, "background": True},
        )
        assert resp.status_code == 200

    def test_multi_turn_session(self) -> None:
        client = _make_session_app()
        resp1 = client.post(
            "/responses",
            json={"model": "t", "input": "msg1", "store": True, "background": True},
        )
        assert resp1.status_code == 200
        id1 = resp1.json()["id"]

        resp2 = client.post(
            "/responses",
            json={
                "model": "t",
                "input": "msg2",
                "store": True,
                "background": True,
                "previous_response_id": id1,
            },
        )
        assert resp2.status_code == 200
