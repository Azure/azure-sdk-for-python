# Copyright (c) Microsoft. All rights reserved.

"""Streaming echo agent supporting both WebSocket and HTTP (SSE) invocations.

Echoes user input back as a stream, sending each word as a separate token chunk.
Supports two communication modes:

- **WebSocket** at ``ws://localhost:8088/websocket/ws``
- **HTTP SSE** at ``POST http://localhost:8088/invocations``

**Server** (this file)::

    python main.py

**WebSocket client** (using the ``websockets`` library)::

    import asyncio, json, websockets

    async def main():
        async with websockets.connect("ws://localhost:8088/websocket/ws") as ws:
            await ws.send(json.dumps({
                "action": "invoke",
                "payload": {"message": "Hello world!"}
            }))
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "stream_chunk":
                    print(msg["payload"]["token"], end=" ", flush=True)
                elif msg["type"] == "stream_end":
                    print("\\nDone!", flush=True)
                    break
                elif msg["type"] == "error":
                    print(f"Error: {msg['error']}")
                    break

    asyncio.run(main())

**HTTP SSE client** (using ``curl``)::

    curl -N -X POST http://localhost:8088/invocations \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Hello world!"}'
"""

import asyncio
import json
from collections.abc import AsyncGenerator

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from azure.ai.agentserver.websocket import WebsocketAgentServerHost, WebsocketContext
from azure.ai.agentserver.invocations import InvocationAgentServerHost

ECHO_PREFIX = "🔊 Echo: "


async def echo_tokens(message: str) -> AsyncGenerator[dict, None]:
    """Yield token dicts with simulated latency (shared by both protocols).

    :param message: The user message to echo.
    :type message: str
    """
    echo_text = f"{ECHO_PREFIX}{message}"
    words = echo_text.split()
    for word in words:
        yield {"token": word}
        await asyncio.sleep(0.1)  # simulate token-by-token latency


# ---------------------------------------------------------------------------InvocationAgentServerHost
# Combined host — Websocket (WebSocket) + Invocations (HTTP/SSE)
# ---------------------------------------------------------------------------


class EchoAgentHost(WebsocketAgentServerHost, InvocationAgentServerHost):
    """Combined host supporting both Invocations (HTTP/SSE) and Websocket (WebSocket).

    Both parent classes store their handler in ``_invoke_fn`` with incompatible
    signatures, so we keep a separate ``_http_invoke_fn`` for the invocations
    endpoint and override ``_dispatch_invoke`` to use it.
    """

    def __init__(self, **kwargs: object) -> None:
        self._http_invoke_fn = None
        super().__init__(**kwargs)

    def http_invoke_handler(self, fn):  # type: ignore[override]
        """Register the HTTP invocation handler."""
        self._http_invoke_fn = fn
        return fn

    async def _dispatch_invoke(self, request: Request) -> Response:
        """Route HTTP invocations to the dedicated HTTP handler."""
        if self._http_invoke_fn is not None:
            return await self._http_invoke_fn(request)
        raise NotImplementedError(
            "No HTTP invoke handler registered. Use @app.http_invoke_handler."
        )


app = EchoAgentHost()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# HTTP SSE invocation endpoint (via azure-ai-agentserver-invocations)
# ---------------------------------------------------------------------------


async def _generate_sse(message: str, invocation_id: str) -> AsyncGenerator[bytes, None]:
    """Yield SSE-formatted token events with simulated latency.

    :param message: The user message to echo.
    :type message: str
    :param invocation_id: The invocation ID for this request.
    :type invocation_id: str
    """
    async for chunk in echo_tokens(message):
        payload = json.dumps(chunk)
        yield f"data: {payload}\n\n".encode()
    done_payload = json.dumps({"invocation_id": invocation_id})
    yield f"event: done\ndata: {done_payload}\n\n".encode()


@app.http_invoke_handler
async def handle_http_invoke(request: Request) -> Response:
    """HTTP invocation endpoint — streams tokens as Server-Sent Events.

    :param request: The incoming HTTP request.
    :type request: ~starlette.requests.Request
    """
    data = await request.json()
    invocation_id = request.state.invocation_id
    message = data.get("message", "Hello! Send me a message and I'll echo it back.")

    return StreamingResponse(
        _generate_sse(message, invocation_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# ---------------------------------------------------------------------------
# WebSocket websocket endpoint (via azure-ai-agentserver-websocket)
# ---------------------------------------------------------------------------


@app.invoke_handler
async def handle_invoke(
    payload: dict, context: WebsocketContext  # pylint: disable=unused-argument
) -> AsyncGenerator[dict, None]:
    """WebSocket streaming handler — each chunk is a ``stream_chunk`` message.

    :param payload: The client request payload.
    :type payload: dict
    :param context: Websocket context with IDs.
    :type context: WebsocketContext
    """
    message = payload.get(
        "message", "Hello! Send me a message and I'll echo it back.")
    async for chunk in echo_tokens(message):
        yield chunk


if __name__ == "__main__":
    app.run()
