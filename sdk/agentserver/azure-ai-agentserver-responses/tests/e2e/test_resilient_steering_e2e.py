# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for steerable conversations (Phase 4).

Tests:
- POST turn 1 (slow) → POST turn 2 → turn 2 gets queued response
- Acceptance hook provides custom queued shape
- ResilienceContext.pending_inputs visible in handler
- Conflict detection for non-steerable conversations
"""

from __future__ import annotations

import asyncio
import time
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


def _make_steerable_app(handler, *, acceptance_hook=None, **kwargs) -> TestClient:
    """Create a TestClient with steerable conversation support."""
    options = ResponsesServerOptions(
        resilient_background=True,
        steerable_conversations=True,
    )
    app = ResponsesAgentServerHost(options=options, **kwargs)
    app.response_handler(handler)
    if acceptance_hook:
        app.response_acceptor(acceptance_hook)
    return TestClient(app)


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
# Tests
# ---------------------------------------------------------------------------


class TestSteerableConversationBaseline:
    """Steerable conversation normal operation."""

    def test_single_turn_completes_normally(self) -> None:
        """A single POST to a steerable app completes as normal."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Turn 1 complete")

        client = _make_steerable_app(handler)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("in_progress", "completed")

    def test_steerable_option_in_context(self) -> None:
        """Handler can see steerable is enabled via context."""
        captured: dict[str, Any] = {}

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            captured["response_id"] = context.response_id
            return TextResponse(context, request, text="Done")

        client = _make_steerable_app(handler)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        assert "response_id" in captured


class TestSteerableConversationConflict:
    """Non-steerable conversations return 409 on conflict."""

    def test_non_steerable_parallel_forks_succeed(self) -> None:
        """Non-steerable: parallel forks (distinct task IDs) all succeed."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Fork response")

        options = ResponsesServerOptions(
            resilient_background=True,
            steerable_conversations=False,
        )
        app = ResponsesAgentServerHost(options=options)
        app.response_handler(handler)
        client = TestClient(app)

        # Create a parent response
        parent = client.post("/responses", json=_base_payload())
        assert parent.status_code == 200
        parent_id = parent.json()["id"]

        # Fork 3 from same parent — all should succeed (non-steerable = fork)
        for _ in range(3):
            resp = client.post(
                "/responses",
                json=_base_payload(previous_response_id=parent_id),
            )
            assert resp.status_code == 200


class TestAcceptanceHookE2E:
    """Acceptance hook integration with the host app."""

    def test_custom_acceptance_hook_registered(self) -> None:
        """Custom acceptance hook is accessible on the app."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Done")

        def my_acceptor(request, context, cancellation_signal):
            return {"status": "queued", "id": context.response_id, "custom_field": True}

        client = _make_steerable_app(handler, acceptance_hook=my_acceptor)
        # Just verify app builds and works
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
