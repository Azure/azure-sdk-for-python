"""HTTP host for the Copilot durable agent with steering.

Wires the Copilot durable task (``agent.py``) to the invocations framework.
With ``steerable=True``, calling ``start()`` on an in-progress task queues
the new input — no manual cancel/wait/restart logic needed.

Requires the **GitHub Copilot SDK** (``pip install github-copilot-sdk``)
and the Copilot CLI installed and authenticated (``gh auth login``).

Usage::

    pip install -r requirements.txt

    python -m durable_copilot.app

    # Turn 1
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Explain Python decorators"}'

    # Poll that invocation
    curl "http://localhost:8088/invocations/<inv-1>"
    # → {"invocation_id": "<inv-1>", "status": "completed", "output": {...}}

    # Steer (while turn 1 is still running)
    curl -X POST "http://localhost:8088/invocations?agent_session_id=demo-001" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Actually, explain async/await instead"}'
"""

from __future__ import annotations

import logging

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from .agent import copilot_session, invocation_store

logger = logging.getLogger(__name__)

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start or steer a Copilot session."""
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

    # Write "queued" to the invocation store before start() — if the task
    # is already running, this input will be queued and the function will
    # overwrite to "running" when it picks it up.  If the task is fresh,
    # the function overwrites to "running" immediately.
    invocation_store.save(invocation_id, {"status": "queued"})

    run = await copilot_session.start(task_id=task_id, input=task_input)

    # Respond with invocation status from the store (queued vs running)
    stored = invocation_store.load(invocation_id)
    status = stored["status"] if stored else "queued"

    return JSONResponse(
        {"invocation_id": invocation_id, "status": status},
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
