"""HTTP host for the durable deep-research agent.

Exposes the ``deep_research`` durable task over the invocations
protocol. Supports both async-poll mode and live SSE streaming:

- ``POST /invocations`` with body ``{"topic": "..."}`` and an
  ``Accept: text/event-stream`` header — returns a live SSE stream of
  token chunks as the research progresses.
- ``POST /invocations`` without the header — returns ``202`` with the
  ``invocation_id``; the caller polls ``GET /invocations/{id}`` for
  status, and once the research completes, gets the assembled report.

Streaming wiring (spec 017):

- ``streams.use_in_memory_replay(...)`` is called once at module
  import (app startup) per streaming.md §7.8 — selects an in-memory
  replay-buffered backing for the registry.
- The HTTP layer extracts ``invocation_id`` from
  ``request.state.invocation_id`` (per-turn identifier per §7.8),
  attaches the SSE subscriber to ``await streams.get_or_create(inv_id)``
  BEFORE invoking the task (subscribe-before-start discipline per
  §5.1), and propagates ``inv_id`` to the handler via
  ``task.start(input={"invocation_id": inv_id, ...})``.
- The handler reads ``ctx.input["invocation_id"]`` and calls
  ``await streams.get_or_create(inv_id)`` — gets the SAME registry-
  cached instance.
- After the task completes, the HTTP layer cleans up via
  ``await streams.delete(inv_id)``.

Recovery: if the container crashes mid-research and is restarted, the
framework re-invokes ``deep_research`` with ``ctx.entry_mode ==
"recovered"`` and the same input — the handler reads its checkpoint
from ``ctx.metadata`` and resumes at the next un-completed stage. The
NEW invocation gets a NEW ``invocation_id`` and a fresh stream — this
is the per-turn scoping per §7.8 (NOT ``task_id`` which survives
recovery).
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamGoneError,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import deep_research, to_sse

logger = logging.getLogger(__name__)

# ── Configure the streams registry once at module import ─────────────────
# In-memory multi-subscriber replay buffer with 10-min sliding window so
# multi-tab subscribers + reconnects within the window get the full
# history. For durable cross-restart streaming, use
# ``streams.use_file_backed_replay(storage_dir=..., ...)`` instead.
streams.use_in_memory_replay(ttl_seconds=600)

app = InvocationAgentServerHost()


async def _sse_from_stream(
    stream: EventStream, invocation_id: str
) -> AsyncGenerator[bytes, None]:
    """Convert an EventStream's payloads into SSE-formatted bytes."""

    yield to_sse(
        {"type": "lifecycle", "status": "running", "invocation_id": invocation_id}
    )

    try:
        async for chunk in stream.subscribe():
            yield to_sse(chunk)
        done = {"type": "done", "invocation_id": invocation_id}
        yield f"event: done\ndata: {json.dumps(done)}\n\n".encode()
    except EventStreamGoneError:
        # Stream destroyed mid-iteration (e.g. another tab called DELETE
        # or the registry GC'd the slot). Emit a clean superseded event.
        superseded = {"type": "superseded", "invocation_id": invocation_id}
        yield f"event: superseded\ndata: {json.dumps(superseded)}\n\n".encode()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    topic: str = data.get("topic", "")
    task_id = f"research-{session_id}"

    # Subscribe-before-start (streaming.md §5.1): create the stream +
    # attach SSE subscriber BEFORE invoking the task. Propagate
    # ``invocation_id`` to the handler via ``ctx.input``.
    stream = await streams.get_or_create(invocation_id)
    await deep_research.start(
        task_id=task_id,
        input={"topic": topic, "invocation_id": invocation_id},
    )

    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            _sse_from_stream(stream, invocation_id),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    return JSONResponse(
        {"invocation_id": invocation_id, "status": "queued", "task_id": task_id},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll the latest checkpointed state for the research task."""

    session_id: str = request.state.session_id
    task_id = f"research-{session_id}"
    info = await deep_research.get(task_id)  # type: ignore[attr-defined]
    if info is None:
        return JSONResponse({"error": "Task not found"}, status_code=404)
    return JSONResponse(
        {
            "task_id": task_id,
            "status": info.status,
            "payload": info.payload,
        }
    )


if __name__ == "__main__":
    app.run()
