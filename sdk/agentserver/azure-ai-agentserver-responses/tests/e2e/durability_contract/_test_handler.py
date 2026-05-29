# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Per-lifetime conformance test handler for the durability-contract suite.

The conformance suite spawns this module as the harness target. It exposes
a deterministic, controllable handler whose timing AND emitted content are
configurable via env vars so individual tests can drive Path A (handler
completes within grace), Path B (grace exhausted), and Path C (SIGKILL).

Every emitted SSE event carries content tagged with the run_attempt
(``L{lifetime}_pre_d{i}`` for pre-sleep deltas, ``L{lifetime}_post_d{i}``
for post-sleep deltas, composite ``L{lifetime}_done|pre=…|post=…|chain=…``
for the terminal text). Tests rely on these tags to verify:

- Pre-crash events survive in the persisted stream after recovery.
- Sequence numbers across recovery attempts are strictly monotonic.
- The recovered handler's output_item slot reuse follows reset semantics.
- ``context.conversation_chain_id`` is stable across attempts.
- ``durability.metadata`` writes from prior lifetimes are visible to the
  recovered handler (when the watermark knob is enabled).

The tags live in :mod:`_test_handler_markers` so tests can import the
formatter without pulling this whole subprocess module.

Env vars consumed:

- ``PORT`` — bound by ``_crash_harness``.
- ``AGENTSERVER_DURABLE_TASKS_PATH`` / ``AGENTSERVER_RESPONSE_STORE_PATH`` /
  ``AGENTSERVER_STREAM_STORE_PATH`` — wired by ``_crash_harness``,
  auto-detected by the responses package.
- ``CONFORMANCE_DURABLE_BACKGROUND`` — ``"true"`` or ``"false"`` to select
  the server's ``durable_background`` option. Default ``"true"``.
- ``CONFORMANCE_STORE_DISABLED`` — ``"true"`` to set ``store_disabled=True``
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
  appends ``context.durability.run_attempt`` to a metadata-stored
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

from tests.e2e.durability_contract._test_handler_markers import (
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


_DURABLE_BG = _env_bool("CONFORMANCE_DURABLE_BACKGROUND", True)
_STORE_DISABLED = _env_bool("CONFORMANCE_STORE_DISABLED", False)
_SLEEP_MS = _env_int("CONFORMANCE_HANDLER_SLEEP_MS", 50)
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))
_PRE_SLEEP_DELTAS = max(0, _env_int("CONFORMANCE_PRE_SLEEP_DELTAS", 0))
_POST_SLEEP_DELTAS = max(0, _env_int("CONFORMANCE_POST_SLEEP_DELTAS", 1))
_EMIT_WATERMARK = _env_bool("CONFORMANCE_EMIT_METADATA_WATERMARK", False)


options = ResponsesServerOptions(
    durable_background=_DURABLE_BG,
    store_disabled=_STORE_DISABLED,
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
       marker per ``durability-contract.md`` § Streaming sub-contract.
    4. Optional metadata watermark write — when enabled, append the
       current ``run_attempt`` to the metadata-stored visited list and
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
    durability = context.durability
    # Lifetime tag: 0 for fresh entry, 1 for any recovered / resumed entry.
    # ``durability.run_attempt`` is an in-process counter that resets to 0
    # on a new process lifetime (i.e. after crash + restart), so it's not
    # a reliable cross-lifetime marker for conformance tests. ``entry_mode``
    # IS preserved across lifetimes — the framework computes it from the
    # task primitive's recovered/resumed signal. Multi-recovery sequences
    # all tag as lifetime=1, which is sufficient for the assertions in
    # this suite (we only need to distinguish "before any crash" from
    # "after at least one crash").
    lifetime = 0 if durability.entry_mode == "fresh" else 1
    chain_id = context.conversation_chain_id or ""

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    if cancellation_signal.is_set():
        return

    # First in_progress is normal; on recovery we emit a second one
    # below as the client-visible reset point per the streaming sub-contract.
    yield stream.emit_in_progress()

    if durability.is_recovery:
        yield stream.emit_in_progress()

    # Optional metadata watermark — append this lifetime's run_attempt
    # to the visited list and flush so the marker survives crash. Tests
    # that enable this knob assert the final text's visited list
    # contains every lifetime that contributed to the response.
    if _EMIT_WATERMARK:
        visited = list(durability.metadata.get(WATERMARK_METADATA_KEY, []))
        if lifetime not in visited:
            visited.append(lifetime)
            durability.metadata[WATERMARK_METADATA_KEY] = visited
            await durability.metadata.flush()

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
        # Shutting down: return without terminal so the framework's
        # per-row Path-B / Path-C contract takes over.
        return

    # Post-sleep deltas — same tagging discipline.
    for j in range(_POST_SLEEP_DELTAS):
        yield text.emit_delta(delta_content(lifetime, PHASE_POST, j))
        await asyncio.sleep(0)

    # Final text — composite of every dimension a test might care about.
    visited_now = (
        list(durability.metadata.get(WATERMARK_METADATA_KEY, []))
        if _EMIT_WATERMARK
        else None
    )
    final = final_text(
        lifetime=lifetime,
        pre_count=_PRE_SLEEP_DELTAS,
        post_count=_POST_SLEEP_DELTAS,
        chain_id=chain_id,
        visited=visited_now,
    )
    yield text.emit_text_done(final)
    yield text.emit_done()
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
