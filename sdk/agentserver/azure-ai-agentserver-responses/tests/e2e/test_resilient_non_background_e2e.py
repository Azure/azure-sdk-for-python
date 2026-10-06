# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient non-background (foreground) sample (Phase 5).

Tests:
- Normal foreground streaming completes
- Foreground non-streaming completes
- Store=true persists the response
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    TextResponse,
)


def _make_foreground_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        for i in range(3):
            for event in stream.output_item_message(f"Part {i + 1}. "):
                yield event
        yield stream.emit_completed()

    return TestClient(app)


def _collect_sse(response) -> list[dict[str, Any]]:
    events = []
    current_type = None
    current_data = None
    for line in response.iter_lines():
        if not line:
            if current_type:
                events.append(
                    {
                        "type": current_type,
                        "data": json.loads(current_data) if current_data else {},
                    }
                )
            current_type = current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type:
        events.append(
            {
                "type": current_type,
                "data": json.loads(current_data) if current_data else {},
            }
        )
    return events


class TestResilientNonBackgroundE2E:
    def test_foreground_streaming_completes(self) -> None:
        """Foreground streaming (background=false) works normally."""
        client = _make_foreground_app()
        payload = {"model": "t", "input": "hi", "stream": True, "store": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            assert resp.status_code == 200
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.created" in types
        assert "response.completed" in types

    def test_foreground_non_streaming(self) -> None:
        """Foreground non-streaming returns completed JSON."""
        options = ResponsesServerOptions(resilient_background=True)
        app = ResponsesAgentServerHost(options=options)

        @app.response_handler
        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Foreground done")

        client = TestClient(app)
        resp = client.post("/responses", json={"model": "t", "input": "hi", "store": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"

    def test_stored_response_retrievable(self) -> None:
        """Stored foreground response is retrievable via GET."""
        client = _make_foreground_app()
        payload = {"model": "t", "input": "hi", "store": True}
        resp = client.post("/responses", json=payload)
        assert resp.status_code == 200
        response_id = resp.json()["id"]

        get_resp = client.get(f"/responses/{response_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == response_id
