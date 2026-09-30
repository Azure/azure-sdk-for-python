# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 032 / B7 conformance handler — recovery precondition TRANSIENT error.

The recovery gate (``_resilient_orchestrator.py``) distinguishes a DEFINITIVE
not-found (``KeyError`` / ``FoundryResourceNotFoundError`` → drop, do not
re-invoke) from a TRANSIENT/ambiguous store error (any other exception → MUST
NOT drop; proceed with ``persisted_response=None`` and re-invoke the handler).

This handler exercises the TRANSIENT branch with no synthetic shortcut:

1. Lifetime 0 persists the response (emits ``response.created``), records a
   marker line, then sleeps in a crash window. The harness SIGKILLs it — so
   the response IS resiliently created (this is NOT a definitive-not-found case).
2. The test then arms a transient fault (writes the arm-marker file) and
   restarts.
3. On the recovered lifetime the framework's persisted-response pre-fetch calls
   ``store.get_response`` — the wrapped store raises a transient ``RuntimeError``
   ONCE (then disarms). The gate MUST catch it, set ``persisted_response=None``,
   and PROCEED — re-invoking the handler, which completes.

The marker file having TWO lines after recovery proves the handler WAS
re-invoked (recovery proceeded, did NOT drop) despite the transient store error.
"""

from __future__ import annotations

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
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.core._config import resolve_state_subdir


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    try:
        return int(raw) if raw is not None else default
    except ValueError:
        return default


_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 10))
_PRE_TERMINAL_SLEEP_MS = _env_int("CONFORMANCE_PRE_TERMINAL_SLEEP_MS", 60000)
_MARKER_FILE = os.environ.get("CONFORMANCE_DROP_MARKER_FILE", "")
_ARM_MARKER = os.environ.get("CONFORMANCE_TRANSIENT_ARM_FILE", "")


class _TransientOnceStore:
    """Wraps a real ``FileResponseStore`` and raises a transient error from
    ``get_response`` exactly once, when the arm-marker file exists. Used to
    drive the recovery gate's transient (MUST NOT drop) branch."""

    def __init__(self, inner: FileResponseStore, arm_marker: str) -> None:
        self._inner = inner
        self._arm_marker = arm_marker

    async def get_response(self, response_id: str, *, context: Any = None) -> Any:
        if self._arm_marker and os.path.exists(self._arm_marker):
            # Disarm first so only the recovery pre-fetch trips; later GET
            # polls (and the test's terminal read) succeed normally.
            try:
                os.remove(self._arm_marker)
            except OSError:
                pass
            raise RuntimeError("injected transient store glitch (recovery pre-fetch)")
        return await self._inner.get_response(response_id, context=context)

    async def create_response(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.create_response(*args, **kwargs)

    async def update_response(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.update_response(*args, **kwargs)

    async def delete_response(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.delete_response(*args, **kwargs)

    async def get_input_items(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.get_input_items(*args, **kwargs)

    async def get_items(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.get_items(*args, **kwargs)

    async def get_history_item_ids(self, *args: Any, **kwargs: Any) -> Any:
        return await self._inner.get_history_item_ids(*args, **kwargs)


options = ResponsesServerOptions(
    resilient_background=True,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
)
_inner_store = FileResponseStore(storage_dir=resolve_state_subdir("responses"))
app = ResponsesAgentServerHost(options=options, store=_TransientOnceStore(_inner_store, _ARM_MARKER))


@app.response_handler
async def handle_create(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    lifetime = 1 if context.is_recovery else 0
    if _MARKER_FILE:
        with open(_MARKER_FILE, "a", encoding="utf-8") as fh:
            fh.write(f"{lifetime}\t{context.response_id}\n")
            fh.flush()
            os.fsync(fh.fileno())

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    # Persist the response (so this is NOT a definitive-not-found case).
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if lifetime == 0:
        # Crash window: the harness SIGKILLs here, AFTER create_response
        # persisted the response.
        await asyncio.sleep(_PRE_TERMINAL_SLEEP_MS / 1000.0)

    # Reached on the recovered lifetime (and the fresh one if no crash):
    # emit a normal terminal.
    message = stream.add_output_item_message()
    yield message.emit_added()
    text = message.add_text_content()
    yield text.emit_added()
    yield text.emit_delta(f"L{lifetime}_done")
    yield text.emit_text_done(f"L{lifetime}_done")
    yield text.emit_done()
    yield message.emit_done()
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
