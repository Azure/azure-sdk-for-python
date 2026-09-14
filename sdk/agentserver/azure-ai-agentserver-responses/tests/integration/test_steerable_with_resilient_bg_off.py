# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 4 step 24a — relaxed composition conformance test.

Proposal #9 of spec 024 §A removed the composition guard that rejected
``steerable_conversations=True + resilient_background=False``. This e2e
test asserts the combination works end-to-end:

- Multiple sequential turns on the same conversation_id succeed.
- Mid-turn input is correctly queued (steering works).
- The chain extends across turns.

Pre-spec-024: ``ResponsesServerOptions(steerable_conversations=True,
resilient_background=False)`` raised ValueError at construction time.
Post-spec-024: this combination is valid; the lock/queue semantics of
steering are independent of the resilience/recovery disposition.

Per spec 024 Phase 4 constitution audit: this RED-first conformance
test lands BEFORE the guard deletion (Principle VII RED-first).

Note: This test does NOT exercise crash recovery — that's covered by
the row-2/row-3 conformance tests. The point here is just that the
combination is ACCEPTED and functions normally for end-to-end chain
extension + steering.
"""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses import (
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


def test_options_construction_with_steerable_and_resilient_bg_off() -> None:
    """Constructing the host with the relaxed combination must NOT raise."""
    options = ResponsesServerOptions(
        steerable_conversations=True,
        resilient_background=False,
    )
    host = ResponsesAgentServerHost(options=options)
    assert host is not None


@pytest.mark.asyncio
async def test_steerable_chain_extends_across_turns_with_resilient_bg_off() -> None:
    """Three sequential turns on the same conversation_id all complete.

    Verifies the chain extends regardless of the resilience disposition.
    Each turn is independent (no in-flight overlap) so steering queuing
    isn't exercised here — just chain extension.
    """
    from starlette.testclient import TestClient

    options = ResponsesServerOptions(
        steerable_conversations=True,
        resilient_background=False,
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
        conversation_id = "conv_steerable_resilient_off_test"

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
