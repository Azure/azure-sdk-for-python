# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for resilient multi-turn conversational agent (Phase 5).

Tests:
- Multi-turn: 3 sequential turns → each references prior context
- Turn counter increments across turns
- Conversation context accumulates
- ResponseContext recovery fields accessible in handler
- Non-resilient fallback works when resilient=False
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
        resilient_background=True,
        steerable_conversations=True,
    )
    app = ResponsesAgentServerHost(options=options)
    state_by_chain: dict[str, dict[str, Any]] = {}

    @app.response_handler
    async def handler(
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ):
        input_text = await context.get_input_text()
        state = state_by_chain.setdefault(context.conversation_chain_id, {})
        turn_count = int(state.get("turn_count", 0)) + 1
        context_list = list(state.get("conversation_context", []))
        context_list.append({"turn": turn_count, "input": input_text})
        state["turn_count"] = turn_count
        state["conversation_context"] = context_list
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


class TestResilientMultiturnBaseline:
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


class TestResilientMultiturnNonResilient:
    """Non-resilient fallback behavior."""

    def test_non_resilient_still_works(self) -> None:
        """With resilient_background=False, handler still functions."""
        options = ResponsesServerOptions(resilient_background=False)
        app = ResponsesAgentServerHost(options=options)

        @app.response_handler
        async def handler(
            request: CreateResponse,
            context: ResponseContext,
            cancellation_signal: asyncio.Event,
        ):
            input_text = await context.get_input_text()
            return TextResponse(context, request, text=f"Non-resilient: {input_text}")

        client = TestClient(app)
        resp = client.post("/responses", json=_base_payload("test"))
        assert resp.status_code == 200


# ════════════════════════════════════════════════════════════════════════════
# Spec 023 row-5 fix — end-to-end depth assertions per Constitution Principle XI.
#
# Row 5 of the per-request matrix is `(store=true, conversation_id=present,
# steerable_conversations=False)`. Pre-spec-023: every turn after the first
# returned 409 conversation_locked because the underlying @task(steerable=False,
# ephemeral=False) registration left the task `status="completed"` after turn 1,
# and the endpoint handler's TaskConflictError→409 mapping caught the
# `completed` status too.
#
# Post-spec-023: the orchestrator routes Row 5 to `@multi_turn_task(steerable=False)`,
# which transitions to `status="suspended"` after each turn. Sequential turns
# extend the chain; only concurrent overlap (handler still in_progress when
# a new turn arrives) returns 409.
#
# These tests close the e2e gap that the unit tests in
# tests/unit/test_conversation_lock.py::TestRow5SequentialTurnsExtendChain
# couldn't cover (unit tests are mocked at the orchestrator-dispatch level).
# Per Constitution Principle XI, the depth assertions verify:
# (a) the chain's actual task status between turns (chain id is shared),
# (b) turn-2's persisted response.output matches the handler's emitted output,
# (c) _responses framework metadata is preserved across the turn boundary.
#
# Uses the real Hypercorn server (via the tests/_helpers fixture) so the
# AgentServerHost's lifespan triggers TaskManager initialization — Starlette's
# TestClient skips lifespan for sync code paths.
# ════════════════════════════════════════════════════════════════════════════


def _make_conv_id_non_steerable_app() -> tuple[Any, dict[str, Any]]:
    """Create an app + handler_state with steerable_conversations=False.

    Returns ``(app, handler_state)``. The caller is responsible for hosting
    the app — typically via ``async with hypercorn_server(app) as client``
    which triggers the lifespan that initialises the TaskManager.
    """
    options = ResponsesServerOptions(
        resilient_background=True,
        steerable_conversations=False,  # Row 5
    )
    app = ResponsesAgentServerHost(options=options)
    handler_state: dict[str, Any] = {"invocations": []}
    turn_count_by_chain: dict[str, int] = {}

    @app.response_handler
    async def handler(
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ):
        input_text = await context.get_input_text()
        chain_id = context.conversation_chain_id
        turn_count = turn_count_by_chain.get(chain_id, 0) + 1
        turn_count_by_chain[chain_id] = turn_count
        handler_state["invocations"].append(
            {
                "input": input_text,
                "turn": turn_count,
                "chain_id": chain_id,
                "entry_mode": "recovered" if context.is_recovery else "fresh",
            }
        )
        return TextResponse(context, request, text=f"chain={chain_id}|turn={turn_count}|input={input_text}")

    return app, handler_state


async def _poll_until_terminal(client: Any, response_id: str, timeout: float = 10.0) -> dict[str, Any]:
    """Poll ``GET /responses/{id}`` until the response reaches terminal."""
    deadline = asyncio.get_event_loop().time() + timeout
    last: dict[str, Any] = {}
    while asyncio.get_event_loop().time() < deadline:
        r = await client.get(f"/responses/{response_id}")
        if r.status_code == 200:
            last = r.json()
            if last.get("status") in ("completed", "failed", "cancelled"):
                return last
        await asyncio.sleep(0.05)
    raise TimeoutError(f"Response {response_id} did not reach terminal within {timeout}s. Last: {last}")


class TestRow5ConversationIdNonSteerableE2E:
    """Spec 023 — Row 5 (`conv_id` + `steerable_conversations=False`) end-to-end."""

    @pytest.mark.asyncio
    async def test_two_sequential_turns_extend_chain_and_complete(self) -> None:
        """Both turns of a `conversation_id` chain succeed; turn 2 sees
        chain-shared metadata; persisted response.output reflects each
        turn's handler-emitted content.

        Depth assertions per Constitution Principle XI:
        - Turn 2's POST returns 200 (NOT 409 conversation_locked).
        - Turn 1 + Turn 2 each produce a `completed` terminal in the
          response store with distinct response_ids.
        - The handler observed `turn_count=1` on turn 1 and `turn_count=2`
          on turn 2 — proving `_responses` metadata persisted across the
          turn boundary (the chain didn't reset).
        - Both turns share the same `conversation_chain_id`.
        - Each turn's persisted `output` text matches what the handler
          emitted for that turn (not just the same generic value).
        """
        from tests._helpers import hypercorn_server

        app, state = _make_conv_id_non_steerable_app()
        conv_id = "conv-row5-sequential"

        async with hypercorn_server(app) as client:
            # Turn 1
            r1 = await client.post("/responses", json=_base_payload("first turn", conversation=conv_id))
            assert r1.status_code == 200, r1.text
            resp1_id = r1.json()["id"]
            terminal1 = await _poll_until_terminal(client, resp1_id)
            assert terminal1["status"] == "completed", terminal1

            # Turn 2 — same conv_id, AFTER turn 1 reached terminal.
            # Under the BUG (pre-spec-023) this returned 409 conversation_locked.
            r2 = await client.post("/responses", json=_base_payload("second turn", conversation=conv_id))
            assert r2.status_code == 200, (
                f"Spec 023 row-5 fix: sequential turns of the same conv_id MUST "
                f"succeed (was 409 pre-fix); got {r2.status_code}: {r2.text}"
            )
            resp2_id = r2.json()["id"]
            assert resp2_id != resp1_id, "Each turn must get a distinct response_id."
            terminal2 = await _poll_until_terminal(client, resp2_id)
            assert terminal2["status"] == "completed", terminal2

        # Depth: handler observed turn_count=1 then turn_count=2 — proves
        # the chain's metadata persisted across the suspend/resume boundary
        # (NOT a reset, which would mean each turn re-starts at turn_count=1).
        invocations = state["invocations"]
        assert len(invocations) == 2, f"Expected 2 invocations, got {invocations}"
        assert invocations[0]["turn"] == 1, invocations[0]
        assert invocations[1]["turn"] == 2, invocations[1]
        # Both turns share the same conversation_chain_id.
        assert (
            invocations[0]["chain_id"] == invocations[1]["chain_id"]
        ), f"Both turns of same conv_id MUST share chain_id; got {invocations}"
        # Each turn's persisted output text contains that turn's input + count
        # (proves the response.output is the actual handler output, not stale).
        out1_text = _extract_text(terminal1)
        out2_text = _extract_text(terminal2)
        assert "turn=1" in out1_text and "first turn" in out1_text, out1_text
        assert "turn=2" in out2_text and "second turn" in out2_text, out2_text

    @pytest.mark.asyncio
    async def test_three_sequential_turns_extend_chain_correctly(self) -> None:
        """Three sequential turns on the same `conversation_id` all succeed;
        the chain extends across each suspend/resume cycle with metadata
        accumulating monotonically.
        """
        from tests._helpers import hypercorn_server

        app, state = _make_conv_id_non_steerable_app()
        conv_id = "conv-row5-triple"

        async with hypercorn_server(app) as client:
            ids: list[str] = []
            for prompt in ("alpha", "beta", "gamma"):
                r = await client.post("/responses", json=_base_payload(prompt, conversation=conv_id))
                assert r.status_code == 200, (
                    f"Sequential turn MUST succeed for conv_id chain; got " f"{r.status_code}: {r.text}"
                )
                rid = r.json()["id"]
                ids.append(rid)
                terminal = await _poll_until_terminal(client, rid)
                assert terminal["status"] == "completed", terminal

        # All 3 distinct response_ids
        assert len(set(ids)) == 3, ids
        # Handler saw monotonically-increasing turn counts: 1, 2, 3
        turn_seq = [inv["turn"] for inv in state["invocations"]]
        assert turn_seq == [1, 2, 3], f"chain metadata must accumulate monotonically; got {turn_seq}"

    @pytest.mark.asyncio
    async def test_concurrent_overlap_still_returns_409(self) -> None:
        """Regression guard: even after the spec-023 fix, concurrent overlap
        on the same `conv_id` (a new turn arrives while a prior turn's
        handler is still `in_progress`) MUST still return 409.

        This is the documented contract per SOT §11.1 — sequential turns
        extend the chain, but two POSTs that overlap in time still race for
        the chain lock.
        """
        from tests._helpers import hypercorn_server
        from azure.ai.agentserver.responses import ResponseEventStream

        options = ResponsesServerOptions(
            resilient_background=True,
            steerable_conversations=False,
        )
        app = ResponsesAgentServerHost(options=options)

        @app.response_handler
        async def handler(request, context, cancellation_signal):
            # Emit response.created IMMEDIATELY (releases the POST's
            # response_created_signal so the POST returns 200), then sleep so
            # the handler stays in_progress while the second POST races.
            stream = ResponseEventStream(
                response_id=context.response_id,
                model=getattr(request, "model", None),
            )
            yield stream.emit_created()
            yield stream.emit_in_progress()
            await asyncio.sleep(1.0)
            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()
            yield tc.emit_delta("done")
            yield tc.emit_text_done("done")
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_completed()

        conv_id = "conv-row5-overlap"

        async with hypercorn_server(app) as client:
            # Turn 1 — POST returns 200 ~immediately (response.created emitted
            # right away), handler then sleeps 1s.
            r1 = await client.post("/responses", json=_base_payload("hold the chain", conversation=conv_id))
            assert r1.status_code == 200, r1.text
            # Wait for the handler to enter its sleep.
            await asyncio.sleep(0.2)
            # Turn 2 — fired while turn 1's handler is still sleeping.
            r2 = await client.post("/responses", json=_base_payload("overlap turn", conversation=conv_id))

        # Turn 2 hit the in-progress lock → 409 conversation_locked.
        assert r2.status_code == 409, (
            f"Concurrent overlap on conv_id MUST return 409 conversation_locked; " f"got {r2.status_code}: {r2.text}"
        )
        err = r2.json().get("error", r2.json())
        assert err.get("code") == "conversation_locked", err
        assert err.get("type") == "conflict", err


def _extract_text(response_body: dict[str, Any]) -> str:
    """Pull all text content out of a response body's output items."""
    out = response_body.get("output") or []
    texts: list[str] = []
    for item in out:
        for part in item.get("content") or []:
            if part.get("type") in ("output_text", "text"):
                texts.append(part.get("text") or "")
    return " ".join(texts)
