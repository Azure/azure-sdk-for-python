# Copyright (c) Microsoft. All rights reserved.

"""Streaming echo agent supporting both WebSocket and HTTP (SSE) conversations.

Echoes user input back as a stream, sending each word as a separate token chunk.
Supports two communication modes:

- **WebSocket** at ``ws://localhost:8088/conversations/ws``
- **HTTP SSE** at ``POST http://localhost:8088/conversations``

**Server** (this file)::

    python main.py

**WebSocket client** (using the ``websockets`` library)::

    import asyncio, json, websockets

    async def main():
        async with websockets.connect("ws://localhost:8088/conversations/ws") as ws:
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

    curl -N -X POST http://localhost:8088/conversations \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Hello world!"}'
"""

import asyncio
import json
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.routing import Route

from azure.ai.agentserver.conversations import ConversationAgentServerHost, ConversationContext

ECHO_PREFIX = "🔊 Echo: "

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


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


# ---------------------------------------------------------------------------
# HTTP SSE conversation endpoint
# ---------------------------------------------------------------------------


async def handle_http_invoke(request: Request) -> Response:
    """HTTP conversation endpoint — streams tokens as Server-Sent Events.

    :param request: The incoming HTTP request.
    :type request: ~starlette.requests.Request
    """
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=_CORS_HEADERS)

    data = await request.json()
    message = data.get("message", "Hello! Send me a message and I'll echo it back.")

    async def generate_sse() -> AsyncGenerator[bytes, None]:
        async for chunk in echo_tokens(message):
            payload = json.dumps(chunk)
            yield f"data: {payload}\n\n".encode()
        yield b"event: done\ndata: {}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={**_CORS_HEADERS, "Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# ---------------------------------------------------------------------------
# Application — WebSocket + HTTP routes
# ---------------------------------------------------------------------------

app = ConversationAgentServerHost(
    routes=[
        Route("/conversations", handle_http_invoke, methods=["POST", "OPTIONS"]),
    ],
)


@app.invoke_handler
async def handle_invoke(
    payload: dict, context: ConversationContext  # pylint: disable=unused-argument
) -> AsyncGenerator[dict, None]:
    """WebSocket streaming handler — each chunk is a ``stream_chunk`` message.

    :param payload: The client request payload.
    :type payload: dict
    :param context: Conversation context with IDs.
    :type context: ConversationContext
    """
    message = payload.get(
        "message", "Hello! Send me a message and I'll echo it back.")
    async for chunk in echo_tokens(message):
        yield chunk


if __name__ == "__main__":
    app.run()
