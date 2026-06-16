"""HTTP host for the durable multi-turn agent.

Wires the durable task (``agent.py``) to the invocations framework.
Per-invocation results are written by the durable task itself (inside the
crash-resilient execution boundary), not by a background collector.

Usage::

    pip install azure-ai-agentserver-invocations

    python -m durable_multiturn.app
    # — or —
    python app.py

    # Turn 1
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "I want to plan a vacation to Japan"}'
    # → 202  (x-agent-invocation-id: <inv-1>)

    # Poll that invocation
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Turn 2
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Budget is $5000, 2 weeks"}'

    # End session
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "done"}'
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.durable import TaskConflictError
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import session_workflow

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or resume a durable session task.

    Each POST is one invocation.  The durable task is an internal detail
    — the caller only sees ``invocation_id`` (from platform headers).

    The task itself writes the invocation result to the store inside the
    durable execution boundary — no background collector needed.
    """
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    message: str = data.get("message", "")
    task_id = f"session-{session_id}"

    try:
        await session_workflow.start(
            task_id=task_id,
            input={
                "session_id": session_id,
                "message": message,
                "invocation_id": invocation_id,
            },
        )
    except TaskConflictError as e:
        return JSONResponse({"error": str(e)}, status_code=409)

    return JSONResponse(
        {"invocation_id": invocation_id, "status": "running"},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll a specific invocation's result.

    Reads the per-invocation result out of ``ctx.metadata`` for the
    current session-level durable task — it was written by the durable
    handler itself inside the execution boundary, so it survives
    crashes.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = f"session-{session_id}"

    # Task.get + TaskSnapshot removed. Use the
    # provider directly for read-only inspection (returns TaskInfo).
    from azure.ai.agentserver.core.durable._manager import get_task_manager

    mgr = get_task_manager()
    info = await mgr.provider.get(task_id)
    if info is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    payload = info.payload or {}
    if payload.get("invocation_id") != invocation_id:
        return JSONResponse({"error": "Invocation not found for this session"}, status_code=404)

    return JSONResponse(
        {
            "invocation_id": invocation_id,
            "status": payload.get("status", info.status),
            "output": payload.get("output"),
        }
    )


if __name__ == "__main__":
    app.run()
