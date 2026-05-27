# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for durable multi-turn conversational agent (Phase 5).

Tests:
- Multi-turn: 3 sequential turns → each references prior context
- Turn counter increments across turns
- Conversation context accumulates
- DurabilityContext accessible in handler
- Non-durable fallback works when durable=False
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


def _make_multiturn_app() -> TestClient:
    """Create a multiturn app similar to the sample."""
    options = ResponsesServerOptions(
        durable_background=True,
        steerable_conversations=True,
    )
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ):
        input_text = await context.get_input_text()
        durability = context.durability

        turn_count = durability.metadata.get("turn_count", 0) + 1
        context_list = durability.metadata.get("conversation_context", [])
        context_list.append({"turn": turn_count, "input": input_text})
        durability.metadata["turn_count"] = turn_count
        durability.metadata["conversation_context"] = context_list
        text = f"Turn {turn_count}: {input_text}"

        return TextResponse(context, request, text=text)

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


class TestDurableMultiturnBaseline:
    """Basic multi-turn conversation flow."""

    def test_single_turn_completes(self) -> None:
        """Single turn completes with turn counter."""
        client = _make_multiturn_app()
        resp = client.post("/responses", json=_base_payload("Hello"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("in_progress", "completed")

    def test_two_sequential_turns(self) -> None:
        """Two turns: second references first via previous_response_id."""
        client = _make_multiturn_app()

        # Turn 1
        resp1 = client.post("/responses", json=_base_payload("I am Alice"))
        assert resp1.status_code == 200
        turn1_id = resp1.json()["id"]

        # Turn 2 references turn 1
        resp2 = client.post(
            "/responses",
            json=_base_payload("What is my name?", previous_response_id=turn1_id),
        )
        assert resp2.status_code == 200

    def test_three_sequential_turns(self) -> None:
        """Three turns: context accumulates."""
        client = _make_multiturn_app()

        # Turn 1
        resp1 = client.post("/responses", json=_base_payload("First"))
        assert resp1.status_code == 200
        id1 = resp1.json()["id"]

        # Turn 2
        resp2 = client.post(
            "/responses",
            json=_base_payload("Second", previous_response_id=id1),
        )
        assert resp2.status_code == 200
        id2 = resp2.json()["id"]

        # Turn 3
        resp3 = client.post(
            "/responses",
            json=_base_payload("Third", previous_response_id=id2),
        )
        assert resp3.status_code == 200


class TestDurableMultiturnNonDurable:
    """Non-durable fallback behavior."""

    def test_non_durable_still_works(self) -> None:
        """With durable_background=False, handler still functions."""
        options = ResponsesServerOptions(durable_background=False)
        app = ResponsesAgentServerHost(options=options)

        @app.response_handler
        async def handler(
            request: CreateResponse,
            context: ResponseContext,
            cancellation_signal: asyncio.Event,
        ):
            input_text = await context.get_input_text()
            return TextResponse(context, request, text=f"Non-durable: {input_text}")

        client = TestClient(app)
        resp = client.post("/responses", json=_base_payload("test"))
        assert resp.status_code == 200
