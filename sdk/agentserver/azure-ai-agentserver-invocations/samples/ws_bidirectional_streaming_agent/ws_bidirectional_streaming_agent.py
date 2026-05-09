"""Bidirectional streaming agent over the ``invocations_ws`` (WebSocket) protocol.

Unlike the request/reply echo in :mod:`samples.ws_invoke_agent`, this sample
exercises the *full-duplex* nature of WebSocket: the server and the client
send and receive on the same socket **concurrently and independently**.

The handler runs three groups of coroutines in parallel:

1. ``_reader``       — consumes inbound JSON frames (prompts and control
                       messages) and dispatches them.  Multiple prompts
                       may arrive while previous ones are still streaming.
2. ``_heartbeat``    — server-initiated push: emits a ``heartbeat`` event
                       every few seconds without any client input.  Proves
                       the outbound direction is not gated on inbound traffic.
3. ``_stream_tokens`` — one task per prompt; streams generated tokens back
                       to the client at its own pace.  Multiple generations
                       can run in parallel; ``cancel`` control messages
                       interrupt them mid-flight.

Wire protocol (JSON over text frames)
-------------------------------------

Inbound (client -> server)::

    {"type": "prompt", "id": "p1", "text": "..."}
    {"type": "cancel", "id": "p1"}
    {"type": "bye"}                 # graceful shutdown

Outbound (server -> client)::

    {"type": "ready"}                          # sent on connect
    {"type": "heartbeat", "ts": 1715200000}    # periodic, server-initiated
    {"type": "token", "id": "p1", "token": "..."}
    {"type": "done",   "id": "p1"}
    {"type": "cancelled", "id": "p1"}
    {"type": "error",  "id": "p1", "message": "..."}

Run it::

    python ws_bidirectional_streaming_agent.py

Drive it with the ``websockets`` CLI; the server keeps streaming heartbeats
and tokens while you type the next prompt::

    python -m websockets ws://localhost:8088/invocations_ws
    > {"type": "prompt", "id": "p1", "text": "Tell me a story"}
    > {"type": "prompt", "id": "p2", "text": "And another"}
    > {"type": "cancel", "id": "p1"}
    > {"type": "bye"}
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost


logger = logging.getLogger("ws_bidirectional_streaming_agent")

app = InvocationAgentServerHost()


# Simulated tokens — in production these would come from a model.
_SIMULATED_TOKENS = [
    "Once", " upon", " a", " time", ",", " in", " a", " land",
    " of", " full", "-", "duplex", " sockets", ",", " a", " server",
    " and", " a", " client", " spoke", " at", " the", " same", " time", ".",
]

_HEARTBEAT_INTERVAL_S = 2.0
_TOKEN_DELAY_S = 0.2


# ---------------------------------------------------------------------------
# HTTP — same host, kept for parity with the rest of the samples.
# ---------------------------------------------------------------------------

@app.invoke_handler  # POST /invocations
async def handle_invoke(request: Request) -> Response:
    """Echo the JSON payload back over HTTP."""
    payload = await request.json()
    return JSONResponse({"echo": payload})


# ---------------------------------------------------------------------------
# WebSocket — true bidirectional streaming.
# ---------------------------------------------------------------------------

async def _generate_tokens(text: str) -> AsyncGenerator[str, None]:
    """Yield simulated tokens with a small per-token delay.

    Replace this with a real streaming model call (e.g. Azure OpenAI) in
    production.

    :param text: The user prompt (unused in this demo).
    :type text: str
    :return: An async generator of token strings.
    :rtype: AsyncGenerator[str, None]
    """
    del text  # demo: ignore prompt content
    for token in _SIMULATED_TOKENS:
        await asyncio.sleep(_TOKEN_DELAY_S)
        yield token


async def _stream_tokens(
    websocket: WebSocket, prompt_id: str, text: str,
) -> None:
    """Stream tokens for one prompt; cancellable via ``asyncio.CancelledError``.

    :param websocket: The accepted WebSocket.
    :type websocket: ~starlette.websockets.WebSocket
    :param prompt_id: Caller-supplied prompt identifier (echoed in events).
    :type prompt_id: str
    :param text: The user prompt to "generate" against.
    :type text: str
    """
    try:
        async for token in _generate_tokens(text):
            await websocket.send_json(
                {"type": "token", "id": prompt_id, "token": token},
            )
        await websocket.send_json({"type": "done", "id": prompt_id})
    except asyncio.CancelledError:
        # Best-effort: tell the client we honoured their cancel.  Suppress
        # any send error (the socket may already be closed) and re-raise
        # so the caller observes the cancellation.
        with contextlib.suppress(Exception):
            await websocket.send_json({"type": "cancelled", "id": prompt_id})
        raise


async def _heartbeat(websocket: WebSocket) -> None:
    """Push a ``heartbeat`` event every ``_HEARTBEAT_INTERVAL_S`` seconds.

    Demonstrates server-initiated traffic that does **not** wait for any
    inbound message — the defining property of full-duplex.

    :param websocket: The accepted WebSocket.
    :type websocket: ~starlette.websockets.WebSocket
    """
    while True:
        await asyncio.sleep(_HEARTBEAT_INTERVAL_S)
        await websocket.send_json(
            {"type": "heartbeat", "ts": int(time.time())},
        )


async def _reader(
    websocket: WebSocket,
    in_flight: "dict[str, asyncio.Task[None]]",
) -> None:
    """Consume inbound frames and dispatch prompt / cancel / bye control messages.

    Returns (instead of raising) on a ``bye`` message or a clean client
    disconnect.  Returning lets the caller cancel the heartbeat task and
    end the connection.

    :param websocket: The accepted WebSocket.
    :type websocket: ~starlette.websockets.WebSocket
    :param in_flight: Map of ``prompt_id`` -> generation task, used to
        honour ``cancel`` messages.
    :type in_flight: dict[str, asyncio.Task[None]]
    """
    try:
        async for raw in websocket.iter_text():
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "invalid JSON"},
                )
                continue

            msg_type = msg.get("type")

            if msg_type == "prompt":
                prompt_id = str(msg.get("id", ""))
                text = str(msg.get("text", ""))
                if not prompt_id:
                    await websocket.send_json(
                        {"type": "error", "message": "prompt requires 'id'"},
                    )
                    continue
                # Schedule the generation as an independent task so it
                # runs in parallel with the reader (and any other
                # in-flight generations).
                task = asyncio.create_task(
                    _stream_tokens(websocket, prompt_id, text),
                    name=f"stream-{prompt_id}",
                )
                in_flight[prompt_id] = task
                task.add_done_callback(
                    lambda _t, k=prompt_id: in_flight.pop(k, None),
                )

            elif msg_type == "cancel":
                prompt_id = str(msg.get("id", ""))
                task = in_flight.get(prompt_id)
                if task is not None and not task.done():
                    task.cancel()

            elif msg_type == "bye":
                return

            else:
                await websocket.send_json(
                    {"type": "error", "message": f"unknown type: {msg_type!r}"},
                )
    except WebSocketDisconnect:
        # Client closed first — let the caller unwind normally.
        return


async def _cancel_and_wait(tasks: "list[asyncio.Task[None]]") -> None:
    """Cancel every task in *tasks* and wait for them to actually finish.

    :param tasks: Tasks to cancel; already-done tasks are ignored.
    :type tasks: list[asyncio.Task[None]]
    """
    for task in tasks:
        if not task.done():
            task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


@app.ws_handler  # /invocations_ws
async def handle_ws(websocket: WebSocket) -> None:
    """Run reader, heartbeat, and per-prompt generation tasks concurrently.

    The SDK has already accepted the connection by the time this function
    runs.  When this coroutine returns the SDK closes the socket with
    code ``1000``; if it raises, the SDK maps the exception to ``1011``.
    """
    await websocket.send_json({"type": "ready"})

    in_flight: "dict[str, asyncio.Task[None]]" = {}
    heartbeat_task = asyncio.create_task(
        _heartbeat(websocket), name="heartbeat",
    )

    try:
        await _reader(websocket, in_flight)
    except WebSocketDisconnect:
        # Client went away mid-read — fall through to cleanup.
        logger.info("client disconnected during streaming")
    finally:
        await _cancel_and_wait(
            [heartbeat_task, *in_flight.values()],
        )


if __name__ == "__main__":
    app.run()
