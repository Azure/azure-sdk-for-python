# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-lifetime conformance test handler for the resilience-contract suite.

The conformance suite spawns this module as the harness target. It exposes
a deterministic, controllable handler whose timing AND emitted content are
configurable via env vars so individual tests can drive Path A (handler
completes within grace), Path B (grace exhausted), and Path C (SIGKILL).

Every emitted SSE event carries content tagged with the retry_attempt
(``L{lifetime}_pre_d{i}`` for pre-sleep deltas, ``L{lifetime}_post_d{i}``
for post-sleep deltas, composite ``L{lifetime}_done|pre=…|post=…|chain=…``
for the terminal text). Tests rely on these tags to verify:

- Pre-crash events survive in the persisted stream after recovery.
- Sequence numbers across recovery attempts are strictly monotonic.
- The recovered handler's output_item slot reuse follows reset semantics.
- ``context.conversation_chain_id`` is stable across attempts.
- ``context.conversation_chain_metadata`` writes from prior lifetimes are visible to the
  recovered handler (when the watermark knob is enabled).

The tags live in :mod:`_test_handler_markers` so tests can import the
formatter without pulling this whole subprocess module.

Env vars consumed:

- ``PORT`` — bound by ``_crash_harness``.
- ``AGENTSERVER_STATE_ROOT`` — wired by ``_crash_harness``, auto-detected
  by both core (resilient tasks) and responses (response store + stream
  store) packages via :func:`azure.ai.agentserver.core._config.resolve_state_subdir`.
  (Spec 024 Phase 3a unified storage layout.)
- ``CONFORMANCE_RESILIENT_BACKGROUND`` — ``"true"`` or ``"false"`` to select
  the server's ``resilient_background`` option. Default ``"true"``.
- ``CONFORMANCE_RESILIENT_BACKGROUND`` — ``"true"`` to set
  ``ResponsesServerOptions(resilient_background=True)``.
  (forces row 4 ephemeral regardless of per-request ``store`` flag).
  Default ``"false"``.
- ``CONFORMANCE_HANDLER_SLEEP_MS`` — milliseconds the handler sleeps
  between the pre-sleep delta burst and the post-sleep delta burst.
  Default ``50`` (fast natural completion).
- ``AGENTSERVER_SHUTDOWN_GRACE_SECONDS`` — server's in-process shutdown
  grace period (integer seconds, minimum 1). Default ``10``.
- ``CONFORMANCE_PRE_SLEEP_DELTAS`` — number of ``output_text.delta`` events
  to emit BEFORE the sleep, on EVERY attempt (fresh and recovered).
  Default ``0``.
- ``CONFORMANCE_POST_SLEEP_DELTAS`` — number of ``output_text.delta`` events
  to emit AFTER the sleep, on EVERY attempt. Default ``1`` so the
  natural completion produces output that matches the historic single-
  ``"ok"``-delta behaviour at the structural level (count and ordering
  match; only the content tags changed).
- ``CONFORMANCE_EMIT_METADATA_WATERMARK`` — when ``"true"``, the handler
  appends ``context.0`` to a metadata-stored
  watermark list and ``flush()``es before emitting deltas. The final
  text includes ``visited=[…]`` so tests can verify the watermark
  survives crash + recovery. Default ``"false"``.
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

from tests.e2e.resilience_contract._test_handler_markers import (
    PHASE_POST,
    PHASE_PRE,
    WATERMARK_METADATA_KEY,
    delta_content,
    final_text,
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
_SLEEP_MS = _env_int("CONFORMANCE_HANDLER_SLEEP_MS", 50)
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))
_PRE_SLEEP_DELTAS = max(0, _env_int("CONFORMANCE_PRE_SLEEP_DELTAS", 0))
_EMIT_WATERMARK = _env_bool("CONFORMANCE_EMIT_METADATA_WATERMARK", False)
# When true, the handler signals shutdown recovery with the explicit
# unified primitive ``await context.exit_for_recovery()`` instead of the
# implicit bare ``return``. Exercises the Spec 025 §A.4 orchestrator
# translation of ``ResponseExitForRecovery`` → next-lifetime recovery.
_EXPLICIT_EXIT_FOR_RECOVERY = _env_bool("CONFORMANCE_EXPLICIT_EXIT_FOR_RECOVERY", False)


options = ResponsesServerOptions(
    resilient_background=_RESILIENT_BG,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
)
app = ResponsesAgentServerHost(options=options)


@app.response_handler
async def handle_create(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Deterministic per-lifetime tagged handler.

    Lifecycle:

    1. ``response.created`` — framework-required first event.
    2. Pre-entry cancellation check — return early if already cancelled.
    3. ``response.in_progress`` — normal start signal. On recovery a
       SECOND ``response.in_progress`` is emitted as the snapshot reset
       marker per ``resilience-contract.md`` § Streaming sub-contract.
    4. Optional metadata watermark write — when enabled, append the
       current ``retry_attempt`` to the metadata-stored visited list and
       ``flush()``. The final text echoes the visited list so tests can
       verify the watermark survives recovery.
    5. ``output_item.added`` + ``content_part.added`` at index 0.
       Always reuses output_index=0 across attempts so tests can verify
       the recovered handler's slot reuse triggers the reset
       reconciliation semantics on the client side.
    6. ``CONFORMANCE_PRE_SLEEP_DELTAS`` deltas with content
       ``L{lifetime}_pre_d{i}``.
    7. Interruptible sleep (``CONFORMANCE_HANDLER_SLEEP_MS``).
    8. Mid-sleep cancellation check — return without terminal if the
       framework signalled cancel / shutdown so the per-row Path B / C
       contract takes over.
    9. ``CONFORMANCE_POST_SLEEP_DELTAS`` deltas with content
       ``L{lifetime}_post_d{i}``.
    10. ``output_text.done`` carrying the composite final text
        ``L{lifetime}_done|pre={N}|post={M}|chain={chain_id}`` (plus
        ``|visited=[…]`` when the watermark knob is enabled).
    11. ``content_part.done`` / ``output_item.done`` / ``response.completed``.
    """
    # Lifetime tag: 0 for fresh entry, 1 for any recovered / resumed entry.
    # ``context.is_recovery`` IS preserved across lifetimes — the framework
    # computes it from the task primitive's recovered signal. Multi-recovery
    # sequences all tag as lifetime=1, which is sufficient for the
    # assertions in this suite (we only need to distinguish "before any
    # crash" from "after at least one crash").
    lifetime = 1 if context.is_recovery else 0
    chain_id = context.conversation_chain_id or ""

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    if cancellation_signal.is_set():
        return

    # First in_progress is normal; on recovery we emit a second one
    # below as the client-visible reset point per the streaming sub-contract.
    yield stream.emit_in_progress()

    if context.is_recovery:
        yield stream.emit_in_progress()

    # Optional metadata watermark — append this lifetime's lifetime tag
    # to the visited list and flush so the marker survives crash. Tests
    # that enable this knob assert the final text's visited list
    # contains every lifetime that contributed to the response.
    if _EMIT_WATERMARK:
        visited = list(context.conversation_chain_metadata.get(WATERMARK_METADATA_KEY, []))
        if lifetime not in visited:
            visited.append(lifetime)
            context.conversation_chain_metadata[WATERMARK_METADATA_KEY] = visited
            await context.conversation_chain_metadata.flush()

    # Output item + content part — always at index 0 so the recovered
    # handler's repeat add at the same index exercises the slot-
    # reconciliation client-side rule.
    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()

    # Pre-sleep deltas — tagged with the lifetime + phase + index so
    # tests can identify which lifetime emitted what content. Yields
    # to the event loop between deltas so each lands on the wire
    # individually rather than being batched.
    for i in range(_PRE_SLEEP_DELTAS):
        yield text.emit_delta(delta_content(lifetime, PHASE_PRE, i))
        await asyncio.sleep(0)

    # Interruptible sleep — either we wake naturally, or shutdown /
    # client-cancel sets the signal.
    try:
        await asyncio.wait_for(
            cancellation_signal.wait(),
            timeout=_SLEEP_MS / 1000.0,
        )
    except asyncio.TimeoutError:
        pass

    if cancellation_signal.is_set():
        # Shutting down: signal next-lifetime recovery. Either via the
        # explicit unified primitive (Spec 025 §A.4) or the implicit
        # bare ``return`` fallback — both leave the response in_progress
        # for the per-row Path-B / Path-C recovery contract.
        if _EXPLICIT_EXIT_FOR_RECOVERY:
            await context.exit_for_recovery()
        return

    # Natural completion: emit the composite final text as a single delta
    # so it accumulates into the response.output snapshot's text field
    # (the framework's snapshot extraction uses delta accumulation, not
    # the emit_text_done payload), then emit text_done with the same
    # value so the wire's done event also carries the composite.
    visited_now = list(context.conversation_chain_metadata.get(WATERMARK_METADATA_KEY, [])) if _EMIT_WATERMARK else None
    final = final_text(
        lifetime=lifetime,
        pre_count=_PRE_SLEEP_DELTAS,
        post_count=1,  # the composite delta itself
        chain_id=chain_id,
        visited=visited_now,
    )
    yield text.emit_delta(final)
    yield text.emit_text_done(final)
    yield text.emit_done()
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
