# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 11 conformance handler — one OutputItem per phase + ``stream.checkpoint()``.

This is the §6 "one OutputItem per phase" resilient pattern made into a
deterministic conformance handler for Spec 025 Row 11 (the
developer-checkpoint-write contract, an extension of Row 1).

Each phase emits exactly one message output item whose text carries a
**per-lifetime-identifiable marker** ``L{lifetime}_phase{n}`` (lifetime 0
on the fresh entry, 1 on any recovered entry). After each phase's
``output_item.done`` the handler ``yield stream.checkpoint()`` — persisting
a snapshot whose ``output`` holds exactly the phases completed so far.

On a recovered entry the handler seeds the stream from
``context.persisted_response`` and resumes at phase
``len(persisted_response.output)`` — so completed (checkpointed) phases are
NOT re-run (they survive with their lifetime-0 marker), and the first
un-checkpointed phase is re-run with the lifetime-1 marker. This makes the
checkpoint contract's central guarantee directly observable in the
recovered ``response.output`` content.

Deterministic crash cutpoints (``CONFORMANCE_CRASH_CUTPOINT``) — applied on
the fresh entry only, so the recovered run always completes:

- ``after_checkpoint:N`` — pause forever right AFTER phase N's checkpoint
  succeeds (snapshot holds N+1 items). A SIGKILL here (Path C) or a SIGTERM
  (Path B) leaves the response recoverable; recovery resumes at phase N+1,
  so phase N survives as ``L0`` and only later phases re-run as ``L1``.
- ``before_checkpoint:N`` — pause forever right AFTER phase N's item is
  emitted but BEFORE its checkpoint. The snapshot still holds N items; a
  crash here re-runs phase N as ``L1``. This is the central guarantee of
  the one-item-per-phase pattern.

Env knobs:

- ``CONFORMANCE_PHASES`` — number of phases (default ``3``).
- ``CONFORMANCE_CRASH_CUTPOINT`` — ``none`` (default) | ``after_checkpoint:N``
  | ``before_checkpoint:N``.
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


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _parse_cutpoint(raw: str | None) -> tuple[str, int] | None:
    """Parse ``after_checkpoint:N`` / ``before_checkpoint:N`` → (kind, N)."""
    if not raw or raw.strip().lower() == "none":
        return None
    kind, _, num = raw.partition(":")
    kind = kind.strip().lower()
    if kind not in ("after_checkpoint", "before_checkpoint"):
        return None
    try:
        return (kind, int(num))
    except ValueError:
        return None


_PHASES = max(1, _env_int("CONFORMANCE_PHASES", 3))
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))
_CRASH_CUTPOINT = _parse_cutpoint(os.environ.get("CONFORMANCE_CRASH_CUTPOINT"))

# Ceiling on the cutpoint pause. Path C SIGKILLs the process during the
# pause; Path B fires shutdown which wakes it. This ceiling is only a
# safety net so a misconfigured run can't hang the suite forever.
_PAUSE_CEILING_S = 30.0


options = ResponsesServerOptions(
    resilient_background=True,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
)
app = ResponsesAgentServerHost(options=options)


async def _pause_at_cutpoint(context: ResponseContext, cancellation_signal: asyncio.Event) -> None:
    """Block at a crash cutpoint until shutdown/cancel fires or the process dies.

    Path C (SIGKILL) kills the process mid-wait — this never returns.
    Path B (SIGTERM short grace) sets ``context.shutdown`` — this returns
    and the caller defers to recovery via ``exit_for_recovery()``.
    """
    shutdown_wait = asyncio.ensure_future(context.shutdown.wait())
    cancel_wait = asyncio.ensure_future(cancellation_signal.wait())
    try:
        await asyncio.wait(
            {shutdown_wait, cancel_wait},
            timeout=_PAUSE_CEILING_S,
            return_when=asyncio.FIRST_COMPLETED,
        )
    finally:
        for fut in (shutdown_wait, cancel_wait):
            if not fut.done():
                fut.cancel()


async def _emit_phase_item(stream: ResponseEventStream, marker: str):
    """Emit one complete message output item carrying ``marker`` as its text."""
    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()
    yield text.emit_delta(marker)
    yield text.emit_text_done(marker)
    yield text.emit_done()
    yield message.emit_done()


@app.response_handler
async def handle_create(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """One-item-per-phase resilient handler with per-phase checkpoints (spec §6).

    Fresh entry (lifetime 0): run every phase, emitting one item per phase
    tagged ``L0_phase{n}`` and ``yield stream.checkpoint()`` after each.

    Recovered entry (lifetime 1): **seed the stream from
    context.persisted_response** so the already-checkpointed phases' items are
    present in ``stream.response.output`` (keeping their original ``L0``
    markers — the checkpoint preserved them), then resume at
    ``len(stream.response.output)`` and run only the remaining phases, tagged
    ``L1_phase{n}``. The persisted response IS the watermark; no replay, no
    breadcrumb reconstruction.
    """
    lifetime = 1 if context.is_recovery else 0

    # Recovery branch: seed from the persisted snapshot (§6). The completed
    # phases' items are already in stream.response.output; count them to know
    # where to resume.
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(
            response_id=context.response_id,
            response=context.persisted_response,
        )
        resume_phase = len(stream.response.output)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        resume_phase = 0

    yield stream.emit_created()  # framework dedups the duplicate on recovery
    # On recovery this in_progress is the client-visible reset point.
    yield stream.emit_in_progress()

    # Remaining phases — fresh work tagged with this lifetime's marker.
    for phase in range(resume_phase, _PHASES):
        async for ev in _emit_phase_item(stream, f"L{lifetime}_phase{phase}"):
            yield ev

        # Cutpoint BEFORE checkpoint (C3) — fresh entry only.
        if not context.is_recovery and _CRASH_CUTPOINT == ("before_checkpoint", phase):
            await _pause_at_cutpoint(context, cancellation_signal)
            # Path B woke us (shutdown). Defer to next-lifetime recovery.
            await context.exit_for_recovery()

        yield stream.checkpoint()

        # Cutpoint AFTER checkpoint (C1) — fresh entry only.
        if not context.is_recovery and _CRASH_CUTPOINT == ("after_checkpoint", phase):
            await _pause_at_cutpoint(context, cancellation_signal)
            await context.exit_for_recovery()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
