"""Streaming invoke agent example (WebSocket).

Demonstrates returning results incrementally via WebSocket streaming.
Callers receive real-time partial output as tokens are generated.

**Server** (this file)::

    python streaming_invoke_agent.py

**Client** (using the ``websockets`` library)::

    import asyncio, json, websockets

    async def main():
        async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
            await ws.send(json.dumps({
                "action": "invoke",
                "payload": {"prompt": "Write a Calculator class with an Add method"}
            }))
            while True:
                msg = json.loads(await ws.recv())
                if msg["type"] == "stream_chunk":
                    print(msg["payload"]["token"], end="", flush=True)
                elif msg["type"] == "stream_end":
                    print("\\nDone!", flush=True)
                    break
                elif msg["type"] == "error":
                    print(f"Error: {msg['error']}")
                    break

    asyncio.run(main())
"""
import asyncio
from collections.abc import AsyncGenerator  # pylint: disable=import-error

from azure.ai.agentserver.invocations import InvocationAgentServerHost, InvocationContext


app = InvocationAgentServerHost()

# Simulated tokens — in production these would come from a model.
_SIMULATED_TOKENS = [
    "class", " Calculator", ":", "\n",
    "    ", "def", " add", "(", "self", ",", " a", ",", " b", ")", ":", "\n",
    "        ", "return", " a", " +", " b", "\n",
]


@app.invoke_handler
async def handle_invoke(
    payload: dict, context: InvocationContext  # pylint: disable=unused-argument
) -> AsyncGenerator[dict, None]:
    """Yield token chunks with simulated latency.

    Each chunk is sent as a WebSocket ``stream_chunk`` message.
    A final ``stream_end`` message signals completion (handled by the framework).

    :param payload: The client request payload (unused in this demo).
    :type payload: dict
    :param context: Invocation context with IDs.
    :type context: InvocationContext
    """
    for token in _SIMULATED_TOKENS:
        yield {"token": token}
        await asyncio.sleep(0.15)  # simulate model latency


if __name__ == "__main__":
    app.run()
