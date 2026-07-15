# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
r"""Sample 19 — Resilient streaming with framework checkpoints.

A resilient response handler with NO upstream framework — recovery is
driven entirely by the framework's own checkpoint primitive
(``stream.checkpoint()`` + ``context.persisted_response``). This is the
canonical teaching shape of the framework-checkpoint recovery strategy;
samples that wrap real upstream frameworks (e.g. LangGraph, ``sample_21``)
compose this with the upstream's own checkpointer.

The handler runs three phases (``analyze`` → ``generate`` → ``refine``)
and emits one output item per phase, calling ``yield stream.checkpoint()``
after each. A checkpoint resiliently persists the response snapshot
(every finished output item, with its original id). On a recovered entry
the handler seeds the stream from ``context.persisted_response`` — so the
already-checkpointed phase items are present in ``stream.response.output``
with their **original ids** — emits ``response.in_progress`` (the
client-visible reset point, re-emitting those same items), and resumes at
``len(stream.response.output)`` (the first phase not yet checkpointed). A
phase interrupted before its checkpoint is simply re-run — correct by
construction, with no watermark bookkeeping and no LLM output stored in
metadata.

Demonstrates:

- The canonical framework-checkpoint pattern (``stream.checkpoint()`` +
  ``context.persisted_response``), one output item per phase.
- ``ResponseEventStream(response=context.persisted_response)`` seeding so
  recovery re-emits the SAME items with their ORIGINAL ids (never invents
  new ids).
- Pre-entry / mid-stream / post-stream cancellation handling.
- ``SIMULATE_SHUTDOWN_MS`` for local mid-stream-shutdown testing.

What this sample does NOT demonstrate (covered by other samples):

- Wrapping a stateful upstream SDK composed with framework checkpoints
  (see ``sample_21`` for LangGraph).
- Steerable multi-turn conversations (see ``sample_20``).

Usage::

    python sample_19_resilient_streaming.py

    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "streamer", "input": "Tell me a joke",
             "stream": true, "store": true, "background": true}'

    # Simulate mid-stream shutdown — handler checkpoints, returns without
    # terminal, framework re-invokes on restart from the last completed phase.
    SIMULATE_SHUTDOWN_MS=120 python sample_19_resilient_streaming.py
"""

import asyncio
import os

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)

options = ResponsesServerOptions(resilient_background=True)
app = ResponsesAgentServerHost(options=options)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))

# Phases run in order. Each emits one message output item and is made
# resilient with a `stream.checkpoint()` after its `output_item.done`.
_PHASE_ORDER: tuple[str, ...] = ("analyze", "generate", "refine")


async def _phase_tokens(phase: str, prompt: str):
    """Simulated upstream — produce a few tokens for the given phase.

    Replace with your real LLM call, document analysis, etc.
    """
    text = {
        "analyze": f"[analyze] Examining input: '{prompt}'.",
        "generate": f"[generate] Drafting response for: '{prompt}'.",
        "refine": f"[refine] Polished result for: '{prompt}'.",
    }[phase]
    for token in text.split():
        await asyncio.sleep(0.03)
        yield token + " "


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Three-phase resilient streaming handler with framework checkpoints."""
    # ── Recovery branch ─────────────────────────────────────────────
    # On recovery, seed the stream from the last resiliently-checkpointed
    # snapshot. The completed phases' items are already in
    # ``stream.response.output`` (carrying their ORIGINAL ids), so we
    # resume from their count. This run's ``response.in_progress`` re-emits
    # those same items and IS the client-visible snapshot reset point
    # (handler guide → Stream Checkpoints).
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=context.persisted_response,
        )
        start = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        start = 0

    yield stream.emit_created()  # library dedups the store write on recovery

    # ── Pre-entry cancellation/shutdown check ──────────────────────
    # This sample does NOT enable steerable_conversations, so STEERED
    # cannot occur. Shutdown and client-cancel are independent, mutually
    # exclusive surfaces — check shutdown FIRST.
    if context.shutdown.is_set():
        # Graceful shutdown before we started: defer to next-lifetime
        # recovery. The unified primitive raises internally and works in
        # this streaming async-generator shape.
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        # Client-cancelled: return without a terminal (framework forces
        # ``cancelled``).
        return

    yield stream.emit_in_progress()

    # Optional local shutdown simulation.
    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(context))

    input_text = await context.get_input_text()

    # Run phases starting at the first one not yet checkpointed.
    for phase in _PHASE_ORDER[start:]:
        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        accumulated = ""
        async for token in _phase_tokens(phase, input_text):
            if cancellation_signal.is_set() or context.shutdown.is_set():
                break
            accumulated += token
            yield text.emit_delta(token)

        # Always close builders for the current phase so the persisted
        # event stream is well-formed even if the phase was cancelled.
        yield text.emit_text_done(accumulated.strip())
        yield text.emit_done()
        yield message.emit_done()

        # ── Mid-stream cancellation/shutdown check ─────────────────
        # If cancelled or shutdown mid-phase, do NOT checkpoint — the phase
        # is not resiliently committed, so a recovered attempt re-runs it.
        if cancellation_signal.is_set() or context.shutdown.is_set():
            break

        # Phase finished cleanly — checkpoint it. The framework persists the
        # response snapshot (this phase's item + all prior), so recovery
        # resumes past it. Backpressured: the write completes before the
        # yield returns.
        yield stream.checkpoint()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Post-stream shutdown check ──────────────────────────────────
    # Shutdown mid-stream: defer to next-lifetime recovery so the
    # framework re-invokes us; the recovery branch above picks up from
    # the last checkpointed phase via ``context.persisted_response``.
    if context.shutdown.is_set():
        await context.exit_for_recovery()

    yield stream.emit_completed()


async def _simulate_shutdown(context: ResponseContext) -> None:
    """Fire SHUTTING_DOWN after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    context.shutdown.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
