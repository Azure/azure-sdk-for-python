"""HTTP host for the LangGraph durable agent.

Wires the LangGraph durable task (``agent.py``) to the invocations framework.
Per-invocation results are written by the durable task itself (inside the
crash-resilient execution boundary), not by a background collector.

Usage::

    pip install -r requirements.txt

    python -m durable_langgraph.app
    # — or —
    python app.py

    # Turn 1
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "I need help planning a trip to Tokyo"}'
    # → 202  (x-agent-invocation-id: <inv-1>)

    # Poll that invocation
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Turn 2
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Budget is $3000 for 10 days"}'

    # End session
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "done"}'
"""

from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.durable import TaskConflictError
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import invocation_store, langgraph_session

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or resume a LangGraph session.

    Each POST is one invocation.  The durable task is internal — the
    caller only sees ``invocation_id`` (from platform headers).

    The task itself writes the invocation result to the store inside the
    durable execution boundary — no background collector needed.
    """
    data = await request.json()
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    message: str = data.get("message", "")
    task_id = f"session-{session_id}"

    try:
        await langgraph_session.start(
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

    Reads from the file-based invocation store — works after restarts.
    Returns the output of **this invocation only** — not the whole session.
    """
    invocation_id: str = request.state.invocation_id

    result = invocation_store.load(invocation_id)
    if result is None:
        return JSONResponse({"error": "Invocation not found"}, status_code=404)

    return JSONResponse({"invocation_id": invocation_id, **result})


if __name__ == "__main__":
    app.run()
