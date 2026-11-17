# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance handler for Spec 026 FR-026-4/5/6/7 — recovery-drop.

This handler crashes (via the harness SIGKILL) **before** it emits
``response.created`` — i.e. before the framework persists the response to
the response store. The resilient task record therefore exists with NO
persisted response. On the next lifetime the recovery scan reclaims the
task, but the responses layer MUST drop it (no re-invocation) because no
client ever received a response id to fetch.

Mechanism (no synthetic shortcuts — a real SIGKILL in the pre-create
window):

1. On EVERY entry, append a line ``"<lifetime>\\t<response_id>\\n"`` to the
   marker file at ``CONFORMANCE_DROP_MARKER_FILE`` — BEFORE any emit. The
   test reads this file to count invocations.
2. Sleep ``CONFORMANCE_PRE_CREATE_SLEEP_MS`` milliseconds **before**
   emitting ``response.created`` — this is the window in which the harness
   SIGKILLs the process, so the crash lands before ``create_response``.
3. Only if the sleep completes (no crash) does the handler emit a normal
   complete response.

The marker file having exactly one entry after crash + restart + recovery
proves the handler was NOT re-invoked (the drop fired). Two entries would
mean recovery wrongly re-invoked an unpersisted response.
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


_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))
_PRE_CREATE_SLEEP_MS = _env_int("CONFORMANCE_PRE_CREATE_SLEEP_MS", 5000)
_MARKER_FILE = os.environ.get("CONFORMANCE_DROP_MARKER_FILE", "")


options = ResponsesServerOptions(
    resilient_background=True,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
)
app = ResponsesAgentServerHost(options=options)


@app.response_handler
async def handle_create(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    lifetime = 1 if context.is_recovery else 0

    # Record this invocation BEFORE any emit so a re-invocation is observable
    # even though the response is never persisted.
    if _MARKER_FILE:
        with open(_MARKER_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{lifetime}\t{context.response_id}\n")
            fh.flush()
            os.fsync(fh.fileno())

    # Crash window: the harness SIGKILLs during this sleep, BEFORE the first
    # emit (and therefore before create_response persists the response).
    await asyncio.sleep(_PRE_CREATE_SLEEP_MS / 1000.0)

    # Only reached if no crash occurred — emit a normal complete response.
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()
    yield text.emit_delta("done")
    yield text.emit_text_done("done")
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
