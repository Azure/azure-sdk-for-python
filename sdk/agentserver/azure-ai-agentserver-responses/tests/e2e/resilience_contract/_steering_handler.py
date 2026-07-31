# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Steerable resilient conformance handler for crash-during-steering tests.

The suite spawns this module as the ``CrashHarness`` target to exercise the
"crash WHILE a steered turn is being drained" resilience scenario (the
follow-up to the retired ``verify_crash_steer`` battery script). It is a
deterministic, steerable variant of ``sample_20`` whose output is tagged so
tests can tell which turn / lifetime produced it.

Steerable semantics (``steerable_conversations=True``): a client steers an
in-flight turn by POSTing a new turn with ``previous_response_id`` pointing at
it. The prior turn observes ``cancellation_signal.is_set()`` with no cause
flag (steering pressure) and ends cleanly with ``emit_completed`` so its
partial output is valid context; the framework then drains the steering input
and runs the new turn.

Per-turn timing knob: after emitting its first delta each turn sleeps
(interruptibly) for ``CONFORMANCE_STEER_SLEEP_MS`` so a SIGKILL can be timed to
land while the *steered* turn is mid-flight.

Output tags (parsed by the test):

- first delta:  ``turn{n}_L{lifetime}_start``
- final text:   ``turn{n}_L{lifetime}_done|input={input_text}``

where ``n`` is the cross-turn ``turn_count`` watermark (survives crash) and
``lifetime`` is ``1`` for any recovered/resumed entry, ``0`` for a fresh one.

Env vars consumed:

- ``PORT`` / ``AGENTSERVER_STATE_ROOT`` — wired by ``_crash_harness``.
- ``CONFORMANCE_RESILIENT_BACKGROUND`` — ``"true"``/``"false"`` (default true).
- ``CONFORMANCE_STEER_SLEEP_MS`` — per-turn interruptible sleep before the
  terminal (default ``4000``); long enough for a mid-flight SIGKILL.
- ``AGENTSERVER_SHUTDOWN_GRACE_SECONDS`` — server shutdown grace (default 10).
"""

from __future__ import annotations

import asyncio
import os

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


_RESILIENT_BG = _env_bool("CONFORMANCE_RESILIENT_BACKGROUND", True)
_STEER_SLEEP_MS = max(0, _env_int("CONFORMANCE_STEER_SLEEP_MS", 4000))
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))


options = ResponsesServerOptions(
    resilient_background=_RESILIENT_BG,
    steerable_conversations=True,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
)
app = ResponsesAgentServerHost(options=options)


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Deterministic steerable resilient handler with a mid-turn sleep."""
    lifetime = 1 if context.is_recovery else 0

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    # Shutdown before start: defer to next-lifetime recovery.
    if context.shutdown.is_set():
        await context.exit_for_recovery()
        return

    # Pre-entry cancellation: steering pressure (a newer turn is queued)
    # ends this turn cleanly; a bare client-cancel returns without terminal.
    if cancellation_signal.is_set():
        if context.pending_input_count > 0:
            yield stream.emit_completed()
        return

    yield stream.emit_in_progress()
    if context.is_recovery:
        # Client-visible reset point for the recovered attempt.
        yield stream.emit_in_progress()

    # Cross-turn watermark — survives crash + turn boundaries.
    turn_count = int(context.conversation_chain_metadata.get("turn_count", 0)) + 1
    context.conversation_chain_metadata["turn_count"] = turn_count
    await context.conversation_chain_metadata.flush()

    input_text = await context.get_input_text()

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    # First delta — the observable "this turn is executing" signal the test
    # waits for before it fires the crash.
    yield text.emit_delta(f"turn{turn_count}_L{lifetime}_start")

    # Interruptible mid-turn sleep. Woken early by steering pressure or
    # shutdown; otherwise a crash lands here while the turn is in-flight.
    try:
        await asyncio.wait_for(cancellation_signal.wait(), timeout=_STEER_SLEEP_MS / 1000.0)
    except asyncio.TimeoutError:
        pass

    if context.shutdown.is_set():
        # Graceful shutdown mid-turn: defer to next-lifetime recovery.
        await context.exit_for_recovery()
        return

    if cancellation_signal.is_set() and context.pending_input_count > 0:
        # Superseded by a newer turn: close cleanly with partial content.
        final = f"turn{turn_count}_L{lifetime}_superseded|input={input_text}"
        yield text.emit_delta(final)
        yield text.emit_text_done(final)
        yield text.emit_done()
        yield message.emit_done()
        yield stream.emit_completed()
        return

    # Natural completion.
    final = f"turn{turn_count}_L{lifetime}_done|input={input_text}"
    yield text.emit_delta(final)
    yield text.emit_text_done(final)
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
