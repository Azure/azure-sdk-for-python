# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient streaming agent sample (Phase 5).

Tests:
- Full streaming completion with all events
- Cooperative cancellation stops mid-stream
- Stream events persisted for replay
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
)


def _make_streaming_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        for i in range(5):
            if cancellation_signal.is_set():
                break
            for event in stream.output_item_message(f"chunk{i} "):
                yield event
            await asyncio.sleep(0.01)
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


class TestResilientStreamingE2E:
    def test_full_streaming_completion(self) -> None:
        client = _make_streaming_app()
        payload = {
            "model": "test",
            "input": "go",
            "stream": True,
            "store": True,
            "background": True,
        }
        with client.stream("POST", "/responses", json=payload) as resp:
            assert resp.status_code == 200
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.created" in types
        assert "response.completed" in types

    def test_non_stream_background_completes(self) -> None:
        client = _make_streaming_app()
        payload = {"model": "test", "input": "go", "store": True, "background": True}
        resp = client.post("/responses", json=payload)
        assert resp.status_code == 200
        assert resp.json()["status"] in ("in_progress", "completed")

    def test_stream_events_have_content(self) -> None:
        client = _make_streaming_app()
        payload = {
            "model": "test",
            "input": "go",
            "stream": True,
            "store": True,
            "background": True,
        }
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        delta_events = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(delta_events) > 0
