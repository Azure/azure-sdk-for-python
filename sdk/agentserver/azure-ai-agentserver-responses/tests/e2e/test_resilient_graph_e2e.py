# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient graph execution sample (Phase 5).

Tests:
- Full graph execution (all nodes) completes
- Graph produces content for each node
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

GRAPH_NODES = ["fetch_data", "transform_data", "generate_output"]


def _make_graph_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        completed = context.conversation_chain_metadata.get("completed_nodes", [])
        start_node = len(completed)

        yield stream.emit_created()
        yield stream.emit_in_progress()

        for i in range(start_node, len(GRAPH_NODES)):
            if cancellation_signal.is_set():
                break
            for event in stream.output_item_message(f"[{GRAPH_NODES[i]}] done. "):
                yield event
            completed = context.conversation_chain_metadata.get("completed_nodes", [])
            completed.append(GRAPH_NODES[i])
            context.conversation_chain_metadata["completed_nodes"] = completed

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


class TestResilientGraphE2E:
    def test_full_graph_execution(self) -> None:
        client = _make_graph_app()
        payload = {
            "model": "t",
            "input": "run",
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
        # Should have delta events for each node
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) >= 3  # At least one per node

    def test_non_stream_graph_completes(self) -> None:
        client = _make_graph_app()
        resp = client.post(
            "/responses",
            json={"model": "t", "input": "run", "store": True, "background": True},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] in ("in_progress", "completed")
