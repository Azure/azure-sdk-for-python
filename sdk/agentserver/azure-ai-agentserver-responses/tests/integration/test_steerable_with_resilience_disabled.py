# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Steerable-conversation compatibility with resilient tasks disabled.

The server accepts ``steerable_conversations=True`` while the core
resilient-tasks switch is disabled. In that mode:

- Multiple sequential turns on the same conversation_id succeed.
- The chain extends across turns.
- Overlapping turns run independently through the asyncio fallback; no
  ``MultiTurnTask`` exists to provide queuing, cancellation, or anti-fork
  semantics.

Applications that need overlapping-turn queuing and anti-fork behavior must
enable resilient tasks before constructing the host.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.responses import (
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


def test_options_construction_with_steerable_and_resilience_disabled() -> None:
    """Constructing the host with the relaxed combination must NOT raise."""
    set_resilient_tasks_enabled(False)
    options = ResponsesServerOptions(
        steerable_conversations=True,
    )
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


@pytest.mark.asyncio
async def test_steerable_chain_extends_with_resilience_disabled() -> None:
    """Three sequential turns on the same conversation_id all complete.

    Verifies chain linkage remains available without claiming that the
    multi-turn task's overlap controls are active.
    """
    from starlette.testclient import TestClient

    set_resilient_tasks_enabled(False)
    options = ResponsesServerOptions(
        steerable_conversations=True,
    )
    host = ResponsesAgentServerHost(options=options)

    @host.response_handler
    async def _handler(request, context, cancellation_signal):  # pylint: disable=unused-argument
        async def _events():
            from azure.ai.agentserver.responses.streaming._event_stream import (
                ResponseEventStream,
            )

            stream = ResponseEventStream(response_id=context.response_id, request=request)
            yield stream.emit_created()
            yield stream.emit_in_progress()
            yield stream.emit_completed()

        return _events()

    with TestClient(host) as client:
        conversation_id = "conv_steerable_resilience_disabled_test"

        # Turn 1
        r1 = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": "turn-1",
                "store": True,
                "background": False,
                "stream": False,
                "conversation_id": conversation_id,
            },
        )
        assert r1.status_code == 200, r1.text
        body1 = r1.json()
        assert body1["status"] == "completed"

        # Turn 2 — extends the chain
        r2 = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": "turn-2",
                "store": True,
                "background": False,
                "stream": False,
                "conversation_id": conversation_id,
                "previous_response_id": body1["id"],
            },
        )
        assert r2.status_code == 200, r2.text
        body2 = r2.json()
        assert body2["status"] == "completed"

        # Turn 3 — chain still extends
        r3 = client.post(
            "/responses",
            json={
                "model": "test-model",
                "input": "turn-3",
                "store": True,
                "background": False,
                "stream": False,
                "conversation_id": conversation_id,
                "previous_response_id": body2["id"],
            },
        )
        assert r3.status_code == 200, r3.text
        assert r3.json()["status"] == "completed"


def test_overlapping_turns_use_independent_fallback_when_resilience_disabled() -> None:
    """Overlapping turns run concurrently without task-backed steering semantics."""
    from starlette.testclient import TestClient

    from azure.ai.agentserver.responses.streaming._event_stream import (
        ResponseEventStream,
    )

    set_resilient_tasks_enabled(False)
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(steerable_conversations=True),
    )
    state = {
        "active": 0,
        "max_active": 0,
        "entries": [],
    }

    @host.response_handler
    async def _handler(request, context, cancellation_signal):
        state["active"] += 1
        state["max_active"] = max(state["max_active"], state["active"])
        state["entries"].append(
            (
                context.is_steered_turn,
                context.pending_input_count,
                cancellation_signal.is_set(),
            )
        )
        try:
            stream = ResponseEventStream(response_id=context.response_id, request=request)
            yield stream.emit_created()
            yield stream.emit_in_progress()
            await asyncio.sleep(0.5)
            yield stream.emit_completed()
        finally:
            state["active"] -= 1

    payload = {
        "model": "test-model",
        "input": "turn-1",
        "store": True,
        "background": True,
        "stream": False,
        "conversation_id": "conv_overlap_resilience_disabled",
    }

    with TestClient(host) as client:
        first = client.post("/responses", json=payload)
        assert first.status_code == 200, first.text
        first_body = first.json()
        assert first_body["status"] == "in_progress"

        second_payload = {
            **payload,
            "input": "turn-2",
            "previous_response_id": first_body["id"],
        }
        second = client.post("/responses", json=second_payload)
        assert second.status_code == 200, second.text
        second_body = second.json()
        assert second_body["status"] == "in_progress"

        assert state["max_active"] == 2
        assert state["entries"] == [(False, 0, False), (False, 0, False)]

        for response_id in (first_body["id"], second_body["id"]):
            for _ in range(20):
                body = client.get(f"/responses/{response_id}").json()
                if body["status"] == "completed":
                    break
                time.sleep(0.05)
            assert body["status"] == "completed", body
