# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Conformance handler for Spec 033 FR-002b — recovered-input parity.

On EVERY entry (fresh lifetime 0 and recovered lifetime 1) the handler records
a digest of everything it observes about the request to a marker file:
``context.request`` fields, ``context.client_headers``,
``context.query_parameters``, and ``context.get_input_items()`` (resolved AND
unresolved). The test compares the lifetime-0 and lifetime-1 digests and asserts
they are byte-for-byte identical — i.e. a recovered handler sees the SAME inputs
it saw on fresh entry (no dropped headers / query / input, no altered request).

Mechanism (real SIGKILL, no synthetic recovery):

1. Record the observed-input digest BEFORE the crash window.
2. Emit ``response.created`` so the response is persisted (recovery
   re-invokes rather than drops).
3. On lifetime 0, sleep so the harness can SIGKILL mid-run.
4. On recovery (lifetime 1) record again, then complete normally.
"""

from __future__ import annotations

import asyncio
import json
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
    try:
        return int(raw) if raw is not None else default
    except ValueError:
        return default


_MARKER_FILE = os.environ.get("CONFORMANCE_PARITY_MARKER_FILE", "")
_SLEEP_MS = _env_int("CONFORMANCE_HANDLER_SLEEP_MS", 60000)
_SHUTDOWN_GRACE_S = max(1, _env_int("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", 30))
# When set, the handler only opens its crash window for a turn whose input
# contains this token — lets a multi-turn test crash a SPECIFIC turn (e.g. turn
# 2) while earlier turns complete normally. Unset → crash window on every
# fresh turn (single-turn tests).
_CRASH_TOKEN = os.environ.get("CONFORMANCE_CRASH_INPUT_TOKEN", "")
_STEERABLE = os.environ.get("CONFORMANCE_STEERABLE", "false").lower() == "true"


options = ResponsesServerOptions(
    resilient_background=True,
    shutdown_grace_period_seconds=_SHUTDOWN_GRACE_S,
    steerable_conversations=_STEERABLE,
)
app = ResponsesAgentServerHost(options=options)


async def _observed(request: CreateResponse, context: ResponseContext) -> dict:
    """Build a stable digest of everything the handler observes about inputs."""
    unresolved = await context.get_input_items(resolve_references=False)
    resolved = await context.get_input_items(resolve_references=True)
    metadata = request.get("metadata")
    return {
        "request_input": request.get("input"),
        "request_model": request.get("model"),
        "request_store": request.get("store"),
        "request_stream": request.get("stream"),
        "request_background": request.get("background"),
        "request_instructions": request.get("instructions"),
        "request_metadata": dict(metadata) if metadata else None,
        "request_conversation": _conv_id(request),
        "request_previous_response_id": request.get("previous_response_id"),
        "client_headers": dict(context.client_headers),
        "query_parameters": dict(context.query_parameters),
        "isolation_user_key": context.platform_context.user_id_key,
        "isolation_chat_key": context.platform_context.call_id,
        "input_text": await context.get_input_text(),
        "input_items_unresolved": [_item_type(i) for i in unresolved],
        "input_items_resolved": [_item_type(i) for i in resolved],
    }


def _item_type(item: object) -> str:
    if isinstance(item, dict):
        value = item.get("type")
        if isinstance(value, str):
            return value
    return type(item).__name__


def _conv_id(request: CreateResponse) -> str | None:
    raw = request.get("conversation")
    if isinstance(raw, str):
        return raw or None
    if isinstance(raw, dict):
        cid = raw.get("id")
        return str(cid) if cid else None
    return None


def _record(lifetime: int, observed: dict) -> None:
    if not _MARKER_FILE:
        return
    with open(_MARKER_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"lifetime": lifetime, "observed": observed}, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


@app.response_handler
async def handle_create(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    lifetime = 1 if context.is_recovery else 0

    # Record what THIS lifetime observed, before any crash window.
    _record(lifetime, await _observed(request, context))

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    # Persist the response so recovery re-invokes (not drops) on the next lifetime.
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if lifetime == 0 and (_CRASH_TOKEN == "" or _CRASH_TOKEN in str(request.get("input"))):
        # Crash window — the harness SIGKILLs here, AFTER response.created
        # persisted but BEFORE the terminal. With a crash token set, only the
        # targeted turn opens this window; earlier turns complete normally.
        await asyncio.sleep(_SLEEP_MS / 1000.0)

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
