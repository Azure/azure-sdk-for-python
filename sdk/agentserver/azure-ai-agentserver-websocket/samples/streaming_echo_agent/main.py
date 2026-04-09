# Copyright (c) Microsoft. All rights reserved.

"""Streaming echo agent using azure-ai-agentserver-invocations (WebSocket).

Echoes user input back as a WebSocket stream,
sending each word as a separate token chunk.

**Server** (this file)::

    python main.py

**Client** (using the ``websockets`` library)::

    import asyncio, json, websockets

    async def main():
        async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
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
"""

import asyncio
from collections.abc import AsyncGenerator

from azure.ai.agentserver.invocations import InvocationAgentServerHost, InvocationContext

ECHO_PREFIX = "🔊 Echo: "

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(
    payload: dict, context: InvocationContext  # pylint: disable=unused-argument
) -> AsyncGenerator[dict, None]:
    """Yield token chunks with simulated latency.

    Each chunk is sent as a WebSocket ``stream_chunk`` message.
    A final ``stream_end`` message signals completion (handled by the framework).

    :param payload: The client request payload.
    :type payload: dict
    :param context: Invocation context with IDs.
    :type context: InvocationContext
    """
    message = payload.get(
        "message", "Hello! Send me a message and I'll echo it back.")
    echo_text = f"{ECHO_PREFIX}{message}"
    words = echo_text.split()

    for word in words:
        yield {"token": word}
        await asyncio.sleep(0.1)  # simulate token-by-token latency


if __name__ == "__main__":
    app.run()
