# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 20 — Durable steering with cancellation × recovery composition.

A steerable durable handler with NO upstream framework. Demonstrates how
the cancellation policy from Spec 011 and the recovery contract from
Spec 012 compose when steering, client cancel, and shutdown interleave
with crash recovery.

Differences from ``sample_19``:

- ``steerable_conversations=True`` — each new turn supersedes the prior
  one; the prior turn's handler observes ``cancellation_reason=STEERED``.
- A single message item per turn (no phases). Recovery within a turn
  doesn't try to checkpoint partial token output — the resumption
  response is empty and the recovered attempt re-streams from scratch.
  This is the realistic case for handlers wrapping non-deterministic
  upstreams (LLMs): you can't pick up exactly where you left off, so
  you start the turn over and let the client redraw on the reset.
- A ``turn_count`` watermark survives across turns; useful for
  conversation-level scaffolding.

What this sample demonstrates:

- Steerable handler that ends a turn cleanly on STEERED (close builders +
  ``emit_completed`` with partial content).
- Mid-stream shutdown returns without terminal — recovery re-runs the
  turn from scratch.
- ``durability.is_recovery`` branch produces an empty resumption response
  that signals the client to reset.
- Cross-turn state via ``turn_count`` survives crashes.

What this sample does NOT demonstrate:

- Per-token checkpointing (impractical for non-deterministic upstreams).
- Wrapping a stateful upstream SDK (see ``sample_17``, ``18``, ``21``).

Usage::

    python sample_20_durable_steering.py

    # Turn 1
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "agent", "input": "Explain quantum computing",
             "store": true, "background": true}'

    # Steer (supersede turn 1)
    curl -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "agent", "input": "Actually explain relativity",
             "store": true, "background": true, "previous_response_id": "<id>"}'

    # Simulate mid-stream shutdown
    SIMULATE_SHUTDOWN_MS=200 python sample_20_durable_steering.py
"""

import asyncio
import os

from azure.ai.agentserver.responses import (
    CancellationReason,
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses.models._generated import ResponseObject

options = ResponsesServerOptions(
    durable_background=True,
    steerable_conversations=True,
)
app = ResponsesAgentServerHost(options=options)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))


async def _simulate_llm_stream(prompt: str):
    """Simulate an LLM producing tokens. Replace with your real LLM call."""
    words = f"Let me explain {prompt} in detail. Comprehensive answer here.".split()
    for word in words:
        await asyncio.sleep(0.05)
        yield word + " "


def _build_resumption_response(
    context: ResponseContext, request: CreateResponse
) -> ResponseObject:
    """Build an empty resumption response.

    For a single-turn handler with a non-deterministic upstream there is
    nothing to safely carry forward from a crashed mid-stream attempt —
    the partial token stream cannot be byte-matched to a re-attempted
    stream, so we discard it and let the recovered attempt produce
    everything fresh. The empty payload tells the client to reset its
    view.
    """
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "output": [],
            "model": request.model,
        }
    )


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Steerable durable handler with cancellation × recovery composition."""
    durability = context.durability

    # ── Recovery branch ─────────────────────────────────────────────
    if durability.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request),
        )
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # ── Phase 1 of cancellation (Spec 011): pre-entry check ────────
    # Signal pre-set on entry — this happens when a newer turn was
    # already queued before we even started.
    if cancellation_signal.is_set():
        if context.cancellation_reason == CancellationReason.STEERED:
            yield stream.emit_completed()
        return

    yield stream.emit_in_progress()

    # Cross-turn state: bump the turn counter. This survives crashes
    # and turn boundaries since it lives in `durability.metadata`.
    turn_count = int(durability.metadata.get("turn_count", 0)) + 1
    durability.metadata["turn_count"] = turn_count

    # Optional local shutdown simulation.
    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(cancellation_signal, context))

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    input_text = await context.get_input_text()
    accumulated = ""

    # ── Phase 2 of cancellation (Spec 011): mid-stream check ──────
    async for token in _simulate_llm_stream(input_text):
        if cancellation_signal.is_set():
            break
        accumulated += token
        yield text.emit_delta(token)

    # Always close builders so the persisted event stream is well-formed
    # — even on a cancelled / steered turn. The partial content is valid
    # context for steerable conversations.
    yield text.emit_text_done(accumulated.strip())
    yield text.emit_done()
    yield message.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Phase 3 of cancellation (Spec 011): post-stream ────────────
    # Shutdown mid-stream: return without terminal so the framework
    # re-invokes us; recovery branch above re-streams from scratch.
    if context.cancellation_reason == CancellationReason.SHUTTING_DOWN:
        return

    # All other cases (steered, client-cancelled, normal completion):
    # emit the terminal event. The framework overrides status for
    # client-cancel; for steered, partial output is valid context.
    yield stream.emit_completed()


async def _simulate_shutdown(cancellation_signal: asyncio.Event, context: ResponseContext) -> None:
    """Fire SHUTTING_DOWN after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    if not cancellation_signal.is_set():
        context.cancellation_reason = CancellationReason.SHUTTING_DOWN
        cancellation_signal.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
