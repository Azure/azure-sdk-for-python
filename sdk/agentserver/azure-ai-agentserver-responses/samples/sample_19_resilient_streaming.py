# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 19 — Resilient streaming with handler-managed phase checkpoints.

A resilient response handler with NO upstream framework — checkpoints are
managed entirely via ``context.conversation_chain_metadata``. This is the teaching shape
of the recovery contract; samples that wrap real upstream frameworks
(Claude, Copilot, LangGraph) layer additional reconciliation on top of
the same pattern.

The handler runs three phases (``analyze`` → ``generate`` → ``refine``)
and emits one output item per phase. After each phase finishes it stamps
``context.conversation_chain_metadata["phase_complete"]``. On a recovered entry, the
handler reads the watermark, builds a resumption response containing the
items for the completed phases, emits ``response.in_progress`` carrying
the resumption response (the client-visible reset point), and resumes at
the first incomplete phase.

Demonstrates:

- The recovery-aware default pattern from the handler guide.
- Resumption response construction from handler-managed metadata only
  (no upstream SDK).
- ``ResponseEventStream(response=resumption)`` seeding.
- Pre-entry / mid-stream / post-stream cancellation handling.
- ``SIMULATE_SHUTDOWN_MS`` for local mid-stream-shutdown testing.

What this sample does NOT demonstrate (covered by other samples):

- Wrapping a stateful upstream SDK (see ``sample_17`` for Claude, ``18``
  for Copilot, ``21`` for LangGraph).
- Steerable multi-turn conversations (see ``sample_20``).

Usage::

    python sample_19_resilient_streaming.py

    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "streamer", "input": "Tell me a joke",
             "stream": true, "store": true, "background": true}'

    # Simulate mid-stream shutdown — handler checkpoints, returns without
    # terminal, framework re-invokes on restart from the last completed phase.
    SIMULATE_SHUTDOWN_MS=120 python sample_19_resilient_streaming.py
"""

import asyncio
import os
from typing import Any

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.responses.models._generated import ResponseObject

options = ResponsesServerOptions(resilient_background=True)
app = ResponsesAgentServerHost(options=options)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))

# Phases run in order. Each emits one message output item and stamps
# `phase_complete` in metadata after the item's `output_item.done`.
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


def _phase_message_payload(phase: str, text: str) -> dict[str, Any]:
    """Serialize a fully-completed phase output item for the resumption response."""
    return {
        "type": "message",
        "id": f"phase_{phase}_msg",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _completed_phase_index(context) -> int:
    """Return the index of the next phase to run; 0 if nothing done yet."""
    done = context.conversation_chain_metadata.get("phase_complete")
    if not done or done not in _PHASE_ORDER:
        return 0
    return _PHASE_ORDER.index(done) + 1


def _build_resumption_response(context: ResponseContext, request: CreateResponse) -> ResponseObject:
    """Build the resumption response from completed phases recorded in metadata.

    Only includes items for phases whose `output_item.done` was emitted in
    a prior attempt. In-flight items from a crashed phase are excluded —
    that phase will be re-run from scratch on this attempt.
    """
    next_phase = _completed_phase_index(context)
    completed_texts = context.conversation_chain_metadata.get("phase_texts", {}) or {}
    output: list[dict[str, Any]] = []
    for phase in _PHASE_ORDER[:next_phase]:
        text = completed_texts.get(phase, "")
        output.append(_phase_message_payload(phase, text))
    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "output": output,
            "model": request.model,
        }
    )


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Three-phase resilient streaming handler with crash recovery."""
    # ── Recovery branch ─────────────────────────────────────────────
    # On recovery, seed the stream with a resumption response derived from
    # metadata watermarks. The library treats this run's ``response.in_progress``
    # as the client-visible snapshot reset (see the handler guide's
    # Resilience section).
    if context.is_recovery:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request),
        )
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()  # library tolerates duplicate on recovery

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
    phase_texts: dict[str, str] = dict(context.conversation_chain_metadata.get("phase_texts", {}) or {})

    # Run phases starting at the first one not yet completed.
    start = _completed_phase_index(context)
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
        # Whether this phase counts as "complete" for recovery purposes
        # is decided below by the watermark.
        yield text.emit_text_done(accumulated.strip())
        yield text.emit_done()
        yield message.emit_done()

        # ── Mid-stream cancellation/shutdown check ─────────────────
        # If cancelled or shutdown mid-phase, do NOT advance the watermark —
        # the phase output is not resiliently committed from a recovery
        # standpoint, and a recovered attempt should re-run this phase.
        if cancellation_signal.is_set() or context.shutdown.is_set():
            break

        # Phase finished cleanly — advance the watermark so a recovery
        # attempt skips this phase. Stamp BEFORE moving on so a crash
        # before the next phase's add still finds this phase complete.
        phase_texts[phase] = accumulated.strip()
        context.conversation_chain_metadata["phase_texts"] = phase_texts
        context.conversation_chain_metadata["phase_complete"] = phase

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Post-stream shutdown check ──────────────────────────────────
    # Shutdown mid-stream: defer to next-lifetime recovery so the
    # framework re-invokes us; the recovery branch above picks up from
    # the last completed phase.
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
