"""HTTP host for the Copilot durable agent with steering and streaming.

Wires the Copilot durable task (``agent.py``) to the invocations framework.
With ``steerable=True``, calling ``start()`` on an in-progress task queues
the new input — no manual cancel/wait/restart logic needed.

**Streaming**: If the POST request includes ``Accept: text/event-stream``,
the response is an SSE stream of text deltas as they are generated.  If the
client disconnects mid-stream, it can fall back to ``GET /invocations/<id>``
which returns the full text snapshot at that moment.

Requires the **GitHub Copilot SDK** (``pip install github-copilot-sdk``)
and the Copilot CLI installed and authenticated (``gh auth login``).

Usage::

    pip install -r requirements.txt

    python -m durable_copilot.app

    # Turn 1 (async)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Explain Python decorators"}'

    # Turn 1 (streaming)
    curl -N -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -H "Accept: text/event-stream" \\
        -d '{"message": "Explain Python decorators"}'

    # Poll (recovery after disconnect)
    curl "http://localhost:8088/invocations/<inv-1>"

    # Steer (while turn 1 is still running)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Actually, explain async/await instead"}'
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamGoneError,
    streams,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import copilot_session, invocation_store

logger = logging.getLogger(__name__)

# Default broadcast (in-memory live) backing: every subscriber attaches
# BEFORE the producer starts (subscribe-before-start — see line 121),
# so we don't need replay catch-up. The recovery path after a streaming
# disconnect is GET /invocations/<id>, which returns the full snapshot
# the Copilot SDK has accumulated upstream — the framework-level replay
# buffer was redundant on top of that and held memory unnecessarily.
# Stream id is the per-turn ``invocation_id`` per streaming.md §7.8.
streams.use_in_memory_live()

app = InvocationAgentServerHost()


async def _sse_from_stream(
    stream: EventStream, invocation_id: str, *, initial_status: str = "queued"
) -> AsyncGenerator[bytes, None]:
    """Convert an EventStream's payloads into SSE-formatted bytes."""

    yield (
        f"data: {json.dumps({'type': 'lifecycle', 'status': initial_status, 'invocation_id': invocation_id})}\n\n"
    ).encode()

    try:
        async for chunk in stream.subscribe():
            yield f"data: {json.dumps(chunk)}\n\n".encode()
        done_data = {"type": "done", "invocation_id": invocation_id}
        yield f"event: done\ndata: {json.dumps(done_data)}\n\n".encode()
    except EventStreamGoneError:
        yield (
            f"event: superseded\n"
            f"data: {json.dumps({'type': 'superseded', 'invocation_id': invocation_id})}\n\n"
        ).encode()
    except Exception as exc:  # pylint: disable=broad-except
        error_data = {
            "type": "error",
            "invocation_id": invocation_id,
            "error": str(exc),
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n".encode()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or steer a Copilot session.

    If ``Accept: text/event-stream`` is set, returns an SSE stream.
    Otherwise returns ``202 Accepted`` for async polling.
    """
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    message: str = data.get("message", "")
    task_id = f"session-{session_id}"

    task_input = {
        "session_id": session_id,
        "message": message,
        "invocation_id": invocation_id,
    }

    invocation_store.save(invocation_id, {"status": "queued"})

    # Subscribe-before-start (streaming.md §5.1): attach SSE subscriber
    # BEFORE starting the task. Handler reads invocation_id from
    # ctx.input and obtains the SAME registry-cached stream.
    stream = await streams.get_or_create(invocation_id)
    await copilot_session.start(task_id=task_id, input=task_input)

    # SSE streaming mode
    wants_stream = "text/event-stream" in request.headers.get("accept", "")
    if wants_stream:
        return StreamingResponse(
            _sse_from_stream(stream, invocation_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # Async mode
    stored = invocation_store.load(invocation_id)
    status = stored["status"] if stored else "queued"

    return JSONResponse(
        {"invocation_id": invocation_id, "status": status},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll a specific invocation's result.

    Returns the current snapshot — during streaming this includes the
    full text generated so far.  This is the recovery path after a
    streaming disconnect.
    """
    invocation_id: str = request.state.invocation_id

    result = invocation_store.load(invocation_id)
    if result is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    return JSONResponse({"invocation_id": invocation_id, **result})


if __name__ == "__main__":
    app.run()
