r"""HTTP host for the LangGraph resilient agent with streaming and steering.

Wires the LangGraph resilient task (``agent.py``) to the invocations framework.
Per-invocation results are written by the resilient task itself (inside the
crash-resilient execution boundary), not by a background collector.

Streaming
~~~~~~~~~

Pass ``Accept: text/event-stream`` on POST to receive an SSE stream of node
progress events (``node_progress``) plus lifecycle events (``queued``,
``running``).  Without the header you get the standard 202 JSON response for
async polling via GET.

Steering is handled by the framework: the resilient task is declared with
``steerable=True``, so calling ``start()`` on an in-progress task **queues**
the new input instead of raising ``TaskConflictError``.  The running function
sees ``ctx.cancel`` set and short-circuits.  The framework then drains the
queue and re-enters the function with the next input.

Usage::

    # From inside this sample directory:
    pip install -r requirements.txt
    python app.py

    # Turn 1 — async
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "I need help planning a trip to Tokyo"}'
    # → 202  (x-agent-invocation-id: <inv-1>)

    # Turn 1 — streaming
    curl -N -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \
        -H "Content-Type: application/json" \
        -H "Accept: text/event-stream" \
        -d '{"message": "I need help planning a trip to Tokyo"}'
    # → SSE stream: lifecycle:queued → lifecycle:running → node_progress → done

    # Poll that invocation (snapshot — always available)
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Steer — send a new invocation while a turn is still running.
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Actually, let us go to Paris instead"}'

    # End session
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "done"}'
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import invocation_store, langgraph_session
except ImportError:  # allows `python app.py` from inside this directory
    from agent import invocation_store, langgraph_session

logger = logging.getLogger(__name__)

# In-memory multi-subscriber replay buffer; 10-min sliding window for
# reconnects within the recovery window. Per streaming.md §7.8 the
# stream id is the per-turn ``invocation_id``.
streams.use_in_memory_replay(ttl_seconds=600)

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
    except EventStreamNotFoundError:
        yield (
            f"event: superseded\n" f"data: {json.dumps({'type': 'superseded', 'invocation_id': invocation_id})}\n\n"
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
    """Start or steer a LangGraph session.

    If ``Accept: text/event-stream`` is set, returns an SSE stream of node
    progress events.  Otherwise returns ``202 Accepted`` for async polling.
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
        "call_id": request.state.call_id,
    }

    await invocation_store.save(
        f"invocation/{invocation_id}",
        {"status": "queued"},
        session_id=session_id,
    )

    # Subscribe-before-start (streaming.md §5.1): attach SSE subscriber
    # BEFORE starting the task. Handler reads invocation_id from
    # ctx.input and obtains the SAME registry-cached stream.
    stream = await streams.get_or_create(invocation_id)
    await langgraph_session.start(task_id=task_id, input=task_input)

    # SSE streaming mode — return live node progress
    wants_stream = "text/event-stream" in request.headers.get("accept", "")
    if wants_stream:
        return StreamingResponse(
            _sse_from_stream(stream, invocation_id),
            media_type="text/event-stream",
            headers={"X-Agent-Invocation-Id": invocation_id},
        )

    # Standard async mode — return 202 with status from store
    stored = await invocation_store.load(f"invocation/{invocation_id}")
    status = stored["status"] if stored else "queued"

    return JSONResponse(
        {"invocation_id": invocation_id, "status": status},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll a specific invocation's snapshot.

    Returns the persisted snapshot from the invocation store.  During streaming
    this includes ``last_node``; after completion it includes full output.
    Use this as the recovery path after an SSE disconnect.
    """
    invocation_id: str = request.state.invocation_id

    result = await invocation_store.load(f"invocation/{invocation_id}")
    if result is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    return JSONResponse({"invocation_id": invocation_id, **result})


if __name__ == "__main__":
    app.run()
