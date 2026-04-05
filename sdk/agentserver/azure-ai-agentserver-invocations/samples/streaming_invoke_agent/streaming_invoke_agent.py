"""Streaming invoke agent example (SSE).

Demonstrates returning results incrementally via Server-Sent Events.
Callers receive real-time partial output as tokens are generated.

Usage::

    # Start the agent
    python streaming_invoke_agent.py

    # Send a streaming request
    curl -N -X POST http://localhost:8088/invocations \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Write a Calculator class with an Add method"}'
    # -> data: {"token": "class"}
    # -> data: {"token": " Calculator"}
    # -> ...
    # -> event: done
    # -> data: {"invocation_id": "..."}
"""
import asyncio
import json
from collections.abc import AsyncGenerator  # pylint: disable=import-error

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


app = InvocationAgentServerHost()

# Simulated tokens — in production these would come from a model.
_SIMULATED_TOKENS = [
    "class", " Calculator", ":", "\n",
    "    ", "def", " add", "(", "self", ",", " a", ",", " b", ")", ":", "\n",
    "        ", "return", " a", " +", " b", "\n",
]


async def _generate_tokens(
    invocation_id: str, prompt: str  # pylint: disable=unused-argument
) -> AsyncGenerator[bytes, None]:
    """Yield SSE-formatted token events with simulated latency.

    Each token is sent as a ``data:`` line per the SSE specification.
    A final ``event: done`` signals stream completion.

    :param invocation_id: The invocation ID for this request.
    :type invocation_id: str
    :param prompt: The user prompt (unused in this demo).
    :type prompt: str
    """
    for token in _SIMULATED_TOKENS:
        payload = json.dumps({"token": token})
        yield f"data: {payload}\n\n".encode()
        await asyncio.sleep(0.15)  # simulate model latency

    # Signal completion
    done_payload = json.dumps({"invocation_id": invocation_id})
    yield f"event: done\ndata: {done_payload}\n\n".encode()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Stream code-generation tokens back to the caller via SSE."""
    data = await request.json()
    invocation_id = request.state.invocation_id
    prompt = data.get("prompt", "")

    return StreamingResponse(
        _generate_tokens(invocation_id, prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


if __name__ == "__main__":
    app.run()
