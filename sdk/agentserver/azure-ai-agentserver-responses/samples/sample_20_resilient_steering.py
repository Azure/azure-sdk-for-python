# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
r"""Sample 20 — Resilient steering with cancellation × recovery composition.

A steerable resilient handler with NO upstream framework. Demonstrates how
the cancellation policy and the crash recovery contract compose when
steering, client cancel, and shutdown interleave with crash recovery.

Differences from ``sample_19``:

- ``steerable_conversations=True`` — each new turn supersedes the prior
  one; the prior turn's handler observes ``context._cancellation_signal.is_set()``
  with no cause flag (steering pressure — neither ``client_cancelled``
  nor ``shutdown.is_set()`` is set).
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
  turn from scratch (the **naive** strategy: no recovery-specific code;
  the fresh ``response.in_progress`` with empty output IS the client reset).
- Cross-turn state via ``turn_count`` survives crashes.

What this sample does NOT demonstrate:

- Framework checkpoints / partial-output recovery (see ``sample_19``).
- Wrapping a stateful upstream SDK composed with framework checkpoints
  (see ``sample_21``).

Usage::

    python sample_20_resilient_steering.py

    # Turn 1
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "agent", "input": "Explain quantum computing",
             "store": true, "background": true}'

    # Steer (supersede turn 1)
    curl -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "agent", "input": "Actually explain relativity",
             "store": true, "background": true, "previous_response_id": "<id>"}'

    # Simulate mid-stream shutdown
    SIMULATE_SHUTDOWN_MS=200 python sample_20_resilient_steering.py
"""

import asyncio
import os

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)

options = ResponsesServerOptions(
    resilient_background=True,
    steerable_conversations=True,
)
app = ResponsesAgentServerHost(options=options)

# Explicitly opt into resilient-task startup recovery, for parity with the
# invocations resilient samples. The Responses framework already registers its
# internal durable tasks at host construction (so recovery runs regardless);
# this call just makes the opt-in intent explicit.
set_resilient_tasks_enabled(True)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))


async def _simulate_llm_stream(prompt: str):
    """Simulate an LLM producing tokens. Replace with your real LLM call."""
    words = f"Let me explain {prompt} in detail. Comprehensive answer here.".split()
    for word in words:
        await asyncio.sleep(0.05)
        yield word + " "


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Steerable resilient handler with cancellation × recovery composition."""
    # ── Recovery: naive re-run ──────────────────────────────────────
    # This handler wraps a non-deterministic upstream and does NOT
    # checkpoint partial output, so recovery needs NO special code: build a
    # fresh stream on every entry (recovered or not). The fresh
    # ``response.in_progress`` (empty output) below IS the client-visible
    # reset — the turn simply re-runs from scratch (guide → naive strategy).
    stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # ── Pre-entry cancellation/shutdown check ────────
    # Shutdown and cancellation are independent, mutually exclusive
    # surfaces — check shutdown FIRST. (Shutdown does NOT fire
    # cancellation_signal.)
    if context.shutdown.is_set():
        # Graceful shutdown before we started: defer to next-lifetime
        # recovery (the framework re-invokes us on restart).
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        if context.pending_input_count > 0:
            # Steering pre-entry: emit completed so the partial output
            # (none in this case) becomes valid context for the drain
            # turn that follows.
            yield stream.emit_completed()
        # Otherwise: client-cancelled (framework forces ``cancelled``) —
        # return silently without a terminal.
        return

    yield stream.emit_in_progress()

    # Cross-turn state lives in an explicit application-owned State Store.
    store = await FoundryStateStore.get_or_create(
        context.conversation_chain_id,
        user_isolation=True,
        description="State for the resilient steering response sample",
    )
    async with store:
        item = await store.get_item("state", call_id=context.platform_context.call_id)
        state = (
            dict(item.value)
            if item is not None and isinstance(item.value, dict)
            else {}
        )
        if state.get("last_response_id") == context.response_id:
            turn_count = int(state.get("turn_count", 1))
        else:
            turn_count = int(state.get("turn_count", 0)) + 1
            await store.set_item(
                "state",
                {"turn_count": turn_count, "last_response_id": context.response_id},
                call_id=context.platform_context.call_id,
            )

    # Optional local shutdown simulation.
    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(context))

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    input_text = await context.get_input_text()
    accumulated = ""

    # ── Mid-stream cancellation/shutdown check ──────
    async for token in _simulate_llm_stream(input_text):
        if cancellation_signal.is_set() or context.shutdown.is_set():
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

    # ── Post-stream shutdown check ────────────────
    # Shutdown mid-stream: defer to next-lifetime recovery so the
    # framework re-invokes us; the recovery branch above re-streams from
    # scratch.
    if context.shutdown.is_set():
        await context.exit_for_recovery()

    # All other cases (steered, client-cancelled, normal completion):
    # emit the terminal event. The framework overrides status for
    # client-cancel; for steered, partial output is valid context.
    yield stream.emit_completed()


async def _simulate_shutdown(context: ResponseContext) -> None:
    """Fire SHUTTING_DOWN after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    context.shutdown.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
