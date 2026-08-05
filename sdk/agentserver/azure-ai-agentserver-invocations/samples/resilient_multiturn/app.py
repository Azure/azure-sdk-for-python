r"""HTTP host for the resilient multi-turn agent.

Wires the resilient task (``agent.py``) to the invocations framework.
Per-invocation results are written by the resilient task itself (inside the
crash-resilient execution boundary), not by a background collector.

Usage::

    # From inside this sample directory:
    pip install -r requirements.txt
    python app.py

    # Turn 1
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "I want to plan a vacation to Japan"}'
    # → 202  (x-agent-invocation-id: <inv-1>)

    # Poll that invocation
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Turn 2
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "Budget is $5000, 2 weeks"}'

    # End session
    curl -X POST "http://localhost:8088/invocations?agent_session_id=trip-001" \
        -H "Content-Type: application/json" \
        -d '{"message": "done"}'
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.tasks import TaskConflictError
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import session_workflow, state_store
except ImportError:  # allows `python app.py` from inside this directory
    from agent import session_workflow, state_store

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or resume a resilient session task.

    Each POST is one invocation.  The resilient task is an internal detail
    — the caller only sees ``invocation_id`` (from platform headers).

    The task itself writes the invocation result to the store inside the
    resilient execution boundary — no background collector needed.
    """
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    message: str = data.get("message", "")
    task_id = f"session-{session_id}"

    await state_store.save(
        f"invocation/{invocation_id}",
        {"status": "queued"},
        session_id=session_id,
    )

    try:
        await session_workflow.start(
            task_id=task_id,
            input={
                "session_id": session_id,
                "message": message,
                "invocation_id": invocation_id,
                "call_id": request.state.call_id,
            },
        )
    except TaskConflictError as e:
        await state_store.save(
            f"invocation/{invocation_id}",
            {"status": "failed", "error": str(e)},
            session_id=session_id,
        )
        return JSONResponse({"error": str(e)}, status_code=409)

    return JSONResponse(
        {"invocation_id": invocation_id, "status": "running"},
        status_code=202,
    )


@app.get_invocation_handler
async def poll_invocation(request: Request) -> Response:
    """Poll a specific invocation's result.

    Reads the per-invocation result from the sample's explicit State Store.
    """
    invocation_id: str = request.state.invocation_id
    result = await state_store.load(f"invocation/{invocation_id}")
    if result is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    return JSONResponse(
        {
            "invocation_id": invocation_id,
            "status": result.get("status", "running"),
            "output": result.get("output"),
        }
    )


if __name__ == "__main__":
    app.run()
