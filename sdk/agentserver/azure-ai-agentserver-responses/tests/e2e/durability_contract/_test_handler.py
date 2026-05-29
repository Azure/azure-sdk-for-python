# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Minimal test handler module for the durability-contract conformance suite.

The conformance suite spawns this module as the harness target. It exposes
a deterministic, controllable handler whose sleep duration and server
options are configured via env vars so individual tests can drive Path A
(handler completes within grace), Path B (grace exhausted), and Path C
(SIGKILL).

The handler is intentionally MINIMAL — no upstream framework dependency.
Its sole purpose is to drive the framework's per-row contract
deterministically.

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
- ``CONFORMANCE_HANDLER_SLEEP_MS`` — milliseconds the handler sleeps before
  emitting completion. Default ``50`` (fast natural completion).
- ``AGENTSERVER_SHUTDOWN_GRACE_SECONDS`` — server's in-process shutdown
  grace period (integer seconds, minimum 1). Default ``10``.
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


_DURABLE_BG = _env_bool("CONFORMANCE_DURABLE_BACKGROUND", True)
_STORE_DISABLED = _env_bool("CONFORMANCE_STORE_DISABLED", False)
_SLEEP_MS = _env_int("CONFORMANCE_HANDLER_SLEEP_MS", 50)
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))


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
    """Deterministic handler — sleep then emit completion.

    Sleep is interruptible via ``cancellation_signal`` so client-cancel
    and server-shutdown propagate. Without interruption, the handler
    sleeps for ``CONFORMANCE_HANDLER_SLEEP_MS`` then emits a single
    output item and a completion terminal.

    Recovery awareness: if ``durability.is_recovery`` is True, emit a
    ``response.in_progress`` reset event first (per the streaming
    sub-contract in ``durability-contract.md`` § Streaming sub-contract),
    then resume the sleep + emit terminal.
    """
    durability = context.durability

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()

    if cancellation_signal.is_set():
        return

    # First in_progress is normal; on recovery we'll emit a second one
    # below as the client-visible reset point per the streaming sub-contract.
    yield stream.emit_in_progress()

    if durability.is_recovery:
        # Recovery reset event — signals reconnecting clients to reset
        # their accumulator. Real handlers may also seed a corrected
        # ``output_items`` here (sample 19 demonstrates the watermark
        # pattern); the conformance suite handler is minimal.
        yield stream.emit_in_progress()

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

    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()
    yield text.emit_delta("ok")
    yield text.emit_text_done("ok")
    yield text.emit_done()
    yield message.emit_done()

    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
