"""HTTP host for the durable deep-research agent.

Exposes the ``deep_research`` durable task over the invocations
protocol. Supports both async-poll mode and live SSE streaming:

- ``POST /invocations`` with body ``{"topic": "..."}`` and an
  ``Accept: text/event-stream`` header — returns a live SSE stream of
  token chunks as the research progresses.
- ``POST /invocations`` without the header — returns ``202`` with the
  ``invocation_id``; the caller polls ``GET /invocations/{id}`` for
  status, and once the research completes, gets the assembled report.

Recovery: if the container crashes mid-research and is restarted, the
framework re-invokes ``deep_research`` with ``ctx.entry_mode ==
"recovered"`` and the same input — the handler reads its checkpoint
from ``ctx.metadata`` and resumes at the next un-completed stage.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import deep_research, to_sse

logger = logging.getLogger(__name__)

app = InvocationAgentServerHost()


async def _sse_from_run(run: object, invocation_id: str) -> AsyncGenerator[bytes, None]:
    """Convert a TaskRun's stream into SSE-formatted bytes."""

    from azure.ai.agentserver.core.durable import (  # pylint: disable=import-outside-toplevel
        TaskCancelled,
        TaskFailed,
        TaskTerminated,
    )

    yield to_sse(
        {"type": "lifecycle", "status": "running", "invocation_id": invocation_id}
    )

    try:
        async for chunk in run:  # type: ignore[union-attr]
            yield to_sse(chunk)

        try:
            result = await run.result()  # type: ignore[union-attr]
            done: dict[str, Any] = {"type": "done", "invocation_id": invocation_id}
            if result is not None and hasattr(result, "output") and result.output is not None:
                done["output"] = result.output
            yield f"event: done\ndata: {json.dumps(done)}\n\n".encode()
        except (TaskCancelled, TaskTerminated):
            yield (
                "event: superseded\n"
                f"data: {json.dumps({'type': 'superseded', 'invocation_id': invocation_id})}\n\n"
            ).encode()
    except TaskFailed as exc:
        err = {"type": "error", "invocation_id": invocation_id, "error": str(exc)}
        yield f"event: error\ndata: {json.dumps(err)}\n\n".encode()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    topic: str = data.get("topic", "")
    task_id = f"research-{session_id}"

    run = await deep_research.start(task_id=task_id, input={"topic": topic})

    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            _sse_from_run(run, invocation_id),
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
