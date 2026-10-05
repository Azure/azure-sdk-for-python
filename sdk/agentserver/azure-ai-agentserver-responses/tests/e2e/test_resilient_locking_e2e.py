# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient conversation locking (Phase 2).

Tests the HTTP-level behavior:
- Steerable: parallel POSTs to same conversation → first 200, second 409
- Non-steerable: parallel forks → all succeed (distinct task IDs)
- resilient_background=False opt-out: no task wrapping, plain asyncio
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(handler, *, resilient: bool = True, steerable: bool = False) -> TestClient:
    """Create a TestClient with configurable resilience options."""
    options = ResponsesServerOptions(
        resilient_background=resilient,
        steerable_conversations=steerable,
    )
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(handler)
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
# Non-steerable: parallel forks all succeed
# ---------------------------------------------------------------------------


class TestNonSteerableParallelForks:
    """Non-steerable mode: each POST gets its own task ID → no conflicts."""

    def test_parallel_forks_all_200(self) -> None:
        """3 POSTs with same previous_response_id, steerable=False → all 200."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Fork result")

        client = _make_app(handler, resilient=True, steerable=False)

        # Create parent
        parent = client.post("/responses", json=_base_payload())
        assert parent.status_code == 200
        parent_id = parent.json()["id"]

        # Fork 3 from same parent — all should succeed
        for _ in range(3):
            resp = client.post(
                "/responses",
                json=_base_payload(previous_response_id=parent_id),
            )
            assert resp.status_code == 200

    def test_distinct_response_ids_on_forks(self) -> None:
        """Each fork gets a unique response ID."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Fork")

        client = _make_app(handler, resilient=True, steerable=False)

        parent = client.post("/responses", json=_base_payload())
        parent_id = parent.json()["id"]

        ids = set()
        for _ in range(3):
            resp = client.post(
                "/responses",
                json=_base_payload(previous_response_id=parent_id),
            )
            ids.add(resp.json()["id"])

        assert len(ids) == 3


# ---------------------------------------------------------------------------
# resilient_background=False opt-out
# ---------------------------------------------------------------------------


class TestResilientOptOut:
    """resilient_background=False: plain asyncio, no task wrapping."""

    def test_non_resilient_still_completes(self) -> None:
        """With resilient_background=False, responses still complete normally."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Non-resilient result")

        client = _make_app(handler, resilient=False, steerable=False)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("in_progress", "completed")

    def test_non_resilient_has_transient_resilience_context(self) -> None:
        """With resilient_background=False, recovery + steering fields are
        flat-defaulted on the context (spec 024 Phase 5 Proposal #10)."""
        captured: dict[str, Any] = {}

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            captured["is_recovery"] = context.is_recovery
            captured["is_steered_turn"] = context.is_steered_turn
            captured["pending_input_count"] = context.pending_input_count
            return TextResponse(context, request, text="Done")

        client = _make_app(handler, resilient=False)
        resp = client.post("/responses", json=_base_payload())
        assert resp.status_code == 200
        # Non-resilient path defaults to a non-recovered fresh entry; flat
        # fields are populated by ResponseContext.__init__.
        assert captured["is_recovery"] is False
        assert captured["is_steered_turn"] is False
        assert captured["pending_input_count"] == 0

    def test_non_resilient_store_false_still_works(self) -> None:
        """store=false + background=false → non-resilient foreground path."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Ephemeral")

        client = _make_app(handler, resilient=True)
        # store=false, background=false → foreground non-resilient
        resp = client.post("/responses", json=_base_payload(store=False, background=False))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestLockingEdgeCases:
    """Edge cases for conversation locking."""

    def test_no_previous_response_id_each_standalone(self) -> None:
        """Without previous_response_id, each request is independent."""

        async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
            return TextResponse(context, request, text="Standalone")

        client = _make_app(handler, resilient=True, steerable=True)

        # Two requests without previous_response_id → both succeed
        resp1 = client.post("/responses", json=_base_payload())
        resp2 = client.post("/responses", json=_base_payload())
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Different response IDs
        assert resp1.json()["id"] != resp2.json()["id"]
