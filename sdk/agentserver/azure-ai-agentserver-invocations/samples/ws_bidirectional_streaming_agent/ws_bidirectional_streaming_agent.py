"""Bidirectional streaming agent over the ``invocations_ws`` (WebSocket) protocol.

Unlike the request/reply echo in :mod:`samples.ws_invoke_agent`, this sample
exercises the *full-duplex* nature of WebSocket: the server and the client
send and receive on the same socket **concurrently and independently**.

The handler runs two groups of coroutines in parallel:

1. ``_reader``       — consumes inbound JSON frames (prompts and control
                       messages) and dispatches them.  Multiple prompts
                       may arrive while previous ones are still streaming.
2. ``_stream_tokens`` — one task per prompt; streams generated tokens back
                       to the client at its own pace.  Multiple generations
                       can run in parallel and run *independently* of any
                       inbound traffic — the defining property of full-
                       duplex.  ``cancel`` control messages interrupt them
                       mid-flight.

.. note::

   Connection keep-alive is **not** an application concern: the SDK can
   ask Hypercorn to send WebSocket protocol-level Ping frames
   (opcode 0x9) on its own schedule (disabled by default; enable by
   setting the ``WS_KEEPALIVE_INTERVAL`` environment variable, surfaced
   on ``AgentConfig.ws_ping_interval``).  When enabled, that is enough
   to survive upstream proxy / load-balancer idle timeouts without your
   handler having to push any application-level heartbeat messages of
   its own.

Wire protocol (JSON over text frames)
-------------------------------------

Inbound (client -> server)::

    {"type": "prompt", "id": "p1", "text": "..."}
    {"type": "cancel", "id": "p1"}
    {"type": "bye"}                 # graceful shutdown

Outbound (server -> client)::

    {"type": "ready"}                            # sent on connect
    {"type": "token", "id": "p1", "token": "..."}
    {"type": "done",   "id": "p1"}
    {"type": "cancelled", "id": "p1"}
    {"type": "error",  "id": "p1", "message": "..."}

Run it::

    python ws_bidirectional_streaming_agent.py

Drive it with the ``websockets`` CLI; the server keeps streaming tokens
for each prompt while you type the next one::

    pip install websockets
    python -m websockets ws://localhost:8088/invocations_ws
    > {"type": "prompt", "id": "p1", "text": "Tell me a story"}
    > {"type": "prompt", "id": "p2", "text": "And another"}
    > {"type": "cancel", "id": "p1"}
    > {"type": "bye"}
"""
import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost


logger = logging.getLogger("azure.ai.agentserver")

app = InvocationAgentServerHost()


# Simulated tokens — in production these would come from a model.
# For real-world streaming patterns, see the streaming examples in
# ``azure-ai-inference`` and ``azure-ai-projects``:
#   https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-inference/samples
#   https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples
_SIMULATED_TOKENS = [
    "Once", " upon", " a", " time", ",", " in", " a", " land",
    " of", " full", "-", "duplex", " sockets", ",", " a", " server",
    " and", " a", " client", " spoke", " at", " the", " same", " time", ".",
]

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

async def _generate_tokens(_text: str) -> AsyncGenerator[str, None]:
    """Yield simulated tokens with a small per-token delay.

    Replace this with a real streaming model call (e.g. Azure OpenAI) in
    production.

    :param _text: The user prompt (unused in this demo — leading underscore
        signals "intentionally ignored" to linters).
    :type _text: str
    :return: An async generator of token strings.
    :rtype: AsyncGenerator[str, None]
    """
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
        # ordinary send errors (the socket may already be closed) and re-raise
        # so the caller observes the cancellation.  We deliberately do NOT
        # catch ``BaseException`` here so process-level signals
        # (``KeyboardInterrupt`` / ``SystemExit``) propagate normally.
        with contextlib.suppress(Exception):
            await websocket.send_json({"type": "cancelled", "id": prompt_id})
        raise
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Surface generation errors to the client as a structured frame so
        # the connection survives a single-prompt failure (parity with the
        # ``error`` reply the reader emits on bad input).
        with contextlib.suppress(Exception):
            await websocket.send_json(
                {"type": "error", "id": prompt_id, "message": str(exc)},
            )
        logger.exception("_stream_tokens failed for prompt %s", prompt_id)


async def _reader(
    websocket: WebSocket,
    in_flight: "dict[str, asyncio.Task[None]]",
) -> None:
    """Consume inbound frames and dispatch prompt / cancel / bye control messages.

    Returns (instead of raising) on a ``bye`` message or a clean client
    disconnect.  Returning lets the caller cancel any in-flight generation
    tasks and end the connection.

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
                # ``k=prompt_id`` captures the current value via a default
                # argument so the callback removes the right entry even if
                # ``prompt_id`` is rebound by a later iteration of the loop.
                task.add_done_callback(
                    lambda _t, k=prompt_id: in_flight.pop(k, None),
                )

            elif msg_type == "cancel":
                prompt_id = str(msg.get("id", ""))
                task = in_flight.get(prompt_id)
                if task is not None and not task.done():
                    task.cancel()
                    # Give the task a brief window to finish its courtesy
                    # ``cancelled`` frame before we move on — prevents the
                    # next prompt from racing against an in-flight close.
                    with contextlib.suppress(
                        asyncio.TimeoutError, asyncio.CancelledError, Exception,
                    ):
                        await asyncio.wait_for(task, timeout=1.0)

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
    """Run the reader and per-prompt generation tasks concurrently.

    The SDK has already accepted the connection by the time this function
    runs, and it is sending WS protocol-level Ping frames on its own
    schedule (see ``AgentConfig.ws_ping_interval``).  When this coroutine
    returns the SDK closes the socket with code ``1000``; if it raises,
    the SDK maps the exception to ``1011``.
    """
    await websocket.send_json({"type": "ready"})

    in_flight: "dict[str, asyncio.Task[None]]" = {}

    try:
        await _reader(websocket, in_flight)
    except WebSocketDisconnect:
        # Client went away mid-read — fall through to cleanup.
        logger.info("client disconnected during streaming")
    finally:
        await _cancel_and_wait(list(in_flight.values()))


if __name__ == "__main__":
    app.run()
