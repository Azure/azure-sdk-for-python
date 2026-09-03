"""Minimal HTTP host for the "hello world" resilient long-running agent.

No streaming — just **start and poll**:

- ``POST /invocations`` with body ``{"name": "...", "steps": N}`` — starts the
  durable task and returns ``202`` with its ``invocation_id``. The task keeps
  running in the background after this response returns.
- ``GET /invocations/{invocation_id}`` — returns a JSON snapshot of the run's
  ``status`` and ``completed_steps`` (read from the durable checkpoint). Poll it
  to watch progress.

Run it::

    pip install -r requirements.txt
    python app.py

Then, in another shell (pass ``?agent_session_id=`` to isolate a run's
checkpoints; GET/cancel must use the same session)::

    # start a run — note the invocation_id in the response (also the
    # X-Agent-Invocation-Id response header)
    curl -s -XPOST -H "Content-Type: application/json" \\
        -d '{"name": "Ada", "steps": 10}' \\
        "http://localhost:8088/invocations?agent_session_id=demo"
    # -> {"status": "started", "invocation_id": "<inv>", "total_steps": 10}

    # poll it (repeat every couple seconds) — same session id
    curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
    # -> {"status": "in_progress", "completed_steps": 3, "total_steps": 10}
    # ... eventually -> {"status": "completed", "completed_steps": 10, ...}
"""

from __future__ import annotations

import json

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import checkpoint_store_name, hello_world
except ImportError:  # allows `python app.py` from inside this directory
    from agent import checkpoint_store_name, hello_world

# Resilient tasks (durable execution + crash recovery) are strictly opt-in as of
# azure-ai-agentserver-core 2.2.0b1: ``AgentServerHost`` builds the
# ``TaskManager`` ONLY when this switch is on, and it must be set before host
# startup (i.e. at module-import time). Without it, ``hello_world.start()``
# raises ``TaskManagerNotInitialized`` and there is no crash recovery — which
# would defeat the purpose of a long-running agent.
set_resilient_tasks_enabled(True)

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start the durable task and return immediately (it runs in the background)."""
    try:
        data = json.loads(await request.body() or b"{}")
    except json.JSONDecodeError:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse(
            {"error": "request body must be a JSON object"}, status_code=400
        )
    name = str(data.get("name", "world"))
    # ``steps`` must be a positive integer: a non-positive count writes no
    # checkpoint, so the accepted invocation would then poll as 404.
    try:
        steps = int(data.get("steps", 10))
    except (TypeError, ValueError):
        return JSONResponse(
            {"error": "steps must be an integer"}, status_code=400
        )
    if steps <= 0:
        return JSONResponse(
            {"error": "steps must be a positive integer"}, status_code=400
        )

    # Key the durable task by this turn's invocation id (the platform-defined
    # identity that GET /invocations/{invocation_id} addresses). The session id
    # scopes the checkpoint store so runs in different sessions cannot collide on
    # a reused invocation id; carry it in the input so recovery uses the same
    # scope.
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id

    # start() schedules the task on the TaskManager and returns right away — the
    # work is NOT tied to this HTTP request's lifetime.
    await hello_world.start(
        task_id=invocation_id,
        input={"name": name, "steps": steps, "session_id": session_id},
    )

    return JSONResponse(
        {"status": "started", "invocation_id": invocation_id, "total_steps": steps},
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Return a JSON status snapshot from the durable checkpoint (poll this)."""
    # The invocations protocol addresses the run by the {invocation_id} path
    # segment, surfaced here as request.state.invocation_id. The session id
    # selects the same session-scoped checkpoint store the task wrote to.
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id

    store = await FoundryStateStore.get_or_create(checkpoint_store_name(session_id))
    try:
        item = await store.get_item(invocation_id)
    finally:
        await store.aclose()

    if item is None:
        # No checkpoint yet. The task may be active but still on its first step
        # (it sleeps before the first checkpoint), so distinguish "running with
        # zero completed steps" from "unknown invocation".
        run = await hello_world.get_active_run(invocation_id)
        if run is not None:
            return JSONResponse(
                {"status": "in_progress", "invocation_id": invocation_id, "completed_steps": 0}
            )
        return JSONResponse(
            {"status": "not_found", "invocation_id": invocation_id}, status_code=404
        )

    value = item.value or {}
    done = int(value.get("completed_steps", 0) or 0)
    total = int(value.get("steps", 0) or 0)
    status = "completed" if total and done >= total else "in_progress"
    return JSONResponse(
        {
            "status": status,
            "invocation_id": invocation_id,
            "completed_steps": done,
            "total_steps": total,
        }
    )


if __name__ == "__main__":
    app.run()
