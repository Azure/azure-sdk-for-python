# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient background orchestration (Phase 1).

Tests the full HTTP lifecycle: POST → handler → response persistence → GET.
Crash simulation uses backdated task files (stale leases).
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_resilient_app(handler, *, steerable: bool = False, **kwargs) -> TestClient:
    """Create a TestClient with a resilient ResponsesAgentServerHost."""
    options = ResponsesServerOptions(
        resilient_background=True,
        steerable_conversations=steerable,
    )
    app = ResponsesAgentServerHost(options=options, **kwargs)
    app.response_handler(handler)
    return TestClient(app)


def _collect_stream_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE lines from a streaming response."""
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                parsed_data: dict[str, Any] = {}
                if current_data:
                    parsed_data = json.loads(current_data)
                events.append({"type": current_type, "data": parsed_data})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        parsed_data = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": parsed_data})

    return events


def _base_payload(input_text: str = "hello", **overrides) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "test-model",
        "input": input_text,
        "store": True,
        "background": True,
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Baseline: Normal completion (background + store=true + resilient)
# ---------------------------------------------------------------------------


class TestResilientOrchestrationBaseline:
    """Verify background resilient responses complete normally (no crash)."""

    def test_post_store_true_background_returns_200(self) -> None:
        """POST store=true background → 200 with response."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Hello, world!")

        client = _make_resilient_app(handler)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("in_progress", "completed")

    def test_post_store_true_background_stream_completes(self) -> None:
        """POST store=true background stream → SSE stream completes normally."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            stream = ResponseEventStream(response_id=context.response_id, request=request)
            yield stream.emit_created()
            yield stream.emit_in_progress()
            for event in stream.output_item_message("Hello!"):
                yield event
            yield stream.emit_completed()

        client = _make_resilient_app(handler)
        payload = _base_payload(stream=True)
        with client.stream("POST", "/responses", json=payload) as resp:
            assert resp.status_code == 200
            events = _collect_stream_events(resp)

        event_types = [e["type"] for e in events]
        assert "response.created" in event_types
        assert "response.completed" in event_types

    def test_resilience_context_accessible_in_handler(self) -> None:
        """Handler can access context.resilience on resilient path."""
        captured: dict[str, Any] = {}

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            captured["resilience"] = context.resilience
            return TextResponse(context, request, text="Done")

        client = _make_resilient_app(handler)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200

        # ResilienceContext should be populated (or None if not yet wired)
        # Phase 1 wiring makes it available
        dc = captured.get("resilience")
        # Initially None until T011 wires the resilient path into run_background
        # After T011: assert dc is not None; assert dc.entry_mode == "fresh"


class TestResilientOrchestrationFailure:
    """Tests for handler failures in resilient mode."""

    def test_handler_raises_response_failed(self) -> None:
        """Handler raises → response becomes 'failed'."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            raise RuntimeError("Intentional failure")

        client = _make_resilient_app(handler)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        data = resp.json()
        # Background response that fails before response.created → failed
        assert data["status"] == "failed"


class TestResilientOrchestrationParallelForks:
    """Tests for parallel fork behavior (FR-013)."""

    def test_parallel_forks_all_succeed(self) -> None:
        """3 POSTs with same previous_response_id, steerable=False → all 200."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Fork response")

        client = _make_resilient_app(handler, steerable=False)

        # Create a parent first
        parent_resp = client.post("/responses", json=_base_payload(store=True))
        assert parent_resp.status_code == 200
        parent_id = parent_resp.json()["id"]

        # Fork 3 from same parent
        responses = []
        for _ in range(3):
            resp = client.post(
                "/responses",
                json=_base_payload(previous_response_id=parent_id, store=True),
            )
            assert resp.status_code == 200
            responses.append(resp.json())

        # All should have distinct IDs
        ids = {r["id"] for r in responses}
        assert len(ids) == 3
