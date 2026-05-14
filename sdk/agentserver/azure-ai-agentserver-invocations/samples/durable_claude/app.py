"""HTTP host for the Claude durable agent with steering and streaming.

Wires the Claude durable task (``agent.py``) to the invocations framework.
With ``steerable=True``, calling ``start()`` on an in-progress task queues
the new input — no manual cancel/wait/restart logic needed.

**Streaming**: If the POST request includes ``Accept: text/event-stream``,
the response is an SSE stream of text deltas as they are generated.  If the
client disconnects mid-stream, it can fall back to ``GET /invocations/<id>``
which returns the full text snapshot at that moment.

Usage::

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY="sk-..."

    python -m durable_claude.app

    # Turn 1 (async — poll for result)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Tell me about quantum computing"}'
    # → 202  {"invocation_id": "...", "status": "running"}

    # Turn 1 (streaming — live text deltas)
    curl -N -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -H "Accept: text/event-stream" \\
        -d '{"message": "Tell me about quantum computing"}'
    # → 200  data: {"type": "text_delta", "delta": "Quantum"}
    #         data: {"type": "text_delta", "delta": " computing"}
    #         ...
    #         event: done
    #         data: {"type": "done", ...}

    # Poll (works after disconnect or for async mode)
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Steer (while turn 1 is still running)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Actually, explain machine learning instead"}'
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import claude_session, invocation_store

logger = logging.getLogger(__name__)

app = InvocationAgentServerHost()


async def _sse_from_run(
    run: object, invocation_id: str, *, initial_status: str = "queued"
) -> AsyncGenerator[bytes, None]:
    """Convert a TaskRun's stream into SSE-formatted bytes.

    Yields lifecycle events (``queued``, ``running``), then ``text_delta``
    chunks, then a terminal event (``done``, ``error``, ``superseded``).

    :param run: The TaskRun handle.
    :param invocation_id: Invocation identifier for event payloads.
    :param initial_status: First lifecycle status to emit (e.g. ``"queued"``).
    """
    from azure.ai.agentserver.core.durable import (  # pylint: disable=import-outside-toplevel
        TaskCancelled,
        TaskFailed,
        TaskTerminated,
    )

    # Emit initial lifecycle event so the caller knows the request was accepted
    yield (
        f"data: {json.dumps({'type': 'lifecycle', 'status': initial_status, 'invocation_id': invocation_id})}\n\n"
    ).encode()

    try:
        async for chunk in run:  # type: ignore[union-attr]
            yield f"data: {json.dumps(chunk)}\n\n".encode()

        # Stream ended normally — get the result
        try:
            result = await run.result()  # type: ignore[union-attr]
            done_data = {
                "type": "done",
                "invocation_id": invocation_id,
            }
            if (
                result is not None
                and hasattr(result, "output")
                and result.output is not None
            ):
                done_data["output"] = result.output
            yield f"event: done\ndata: {json.dumps(done_data)}\n\n".encode()
        except (TaskCancelled, TaskTerminated):
            yield (
                f"event: superseded\n"
                f"data: {json.dumps({'type': 'superseded', 'invocation_id': invocation_id})}\n\n"
            ).encode()
    except TaskFailed as exc:
        error_data = {
            "type": "error",
            "invocation_id": invocation_id,
            "error": str(exc),
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n".encode()
    except Exception as exc:  # pylint: disable=broad-except
        error_data = {
            "type": "error",
            "invocation_id": invocation_id,
            "error": str(exc),
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n".encode()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or steer a Claude session.

    If ``Accept: text/event-stream`` is set, returns an SSE stream of
    text deltas.  Otherwise returns ``202 Accepted`` for async polling.
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

    run = await claude_session.start(task_id=task_id, input=task_input)

    # SSE streaming mode — return live text deltas
    wants_stream = "text/event-stream" in request.headers.get("accept", "")
    if wants_stream:
        return StreamingResponse(
            _sse_from_run(run, invocation_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # Async mode — return 202 and let client poll
    stored = invocation_store.load(invocation_id)
    status = stored["status"] if stored else "queued"

    return JSONResponse(
        {"invocation_id": invocation_id, "status": status},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll a specific invocation's result.

    Returns the current snapshot — during streaming this includes
    ``{"status": "streaming", "text": "..."}`` with the full text
    generated so far.  After completion, returns the final output.

    This is the recovery path: if a streaming client disconnects,
    it switches to polling to get the accumulated text.
    """
    invocation_id: str = request.state.invocation_id

    result = invocation_store.load(invocation_id)
    if result is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    return JSONResponse({"invocation_id": invocation_id, **result})


if __name__ == "__main__":
    app.run()
