"""Minimal HTTP host for the "hello world" resilient long-running agent.

No streaming — just **start and poll**:

- ``POST /invocations`` with body ``{"name": "...", "steps": N}`` — starts the
  durable task and returns ``202`` with its ``task_id``. The task keeps running
  in the background after this response returns.
- ``GET /invocations/{id}?task_id=<task_id>`` — returns a JSON snapshot of the
  run's ``status`` and ``completed_steps`` (read from the durable checkpoint).
  Poll it to watch progress.

Run it::

    pip install -r requirements.txt
    python app.py

Then, in another shell::

    # start a run
    curl -s -XPOST -H "Content-Type: application/json" \\
        -d '{"name": "Ada", "steps": 10}' http://localhost:8088/invocations
    # -> {"status": "started", "task_id": "hello-<session>", "total_steps": 10}

    # poll it (repeat every couple seconds)
    curl -s "http://localhost:8088/invocations/x?task_id=hello-<session>"
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
    from .agent import CHECKPOINT_STORE, hello_world
except ImportError:  # allows `python app.py` from inside this directory
    from agent import CHECKPOINT_STORE, hello_world

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
        data = {}
    name = str(data.get("name", "world"))
    steps = int(data.get("steps", 10))

    session_id: str = request.state.session_id
    task_id = f"hello-{session_id}"

    # start() schedules the task on the TaskManager and returns right away — the
    # work is NOT tied to this HTTP request's lifetime.
    await hello_world.start(task_id=task_id, input={"name": name, "steps": steps})

    return JSONResponse(
        {"status": "started", "task_id": task_id, "total_steps": steps},
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Return a JSON status snapshot from the durable checkpoint (poll this)."""
    # Poll by the task_id returned from POST; fall back to this request's session.
    task_id = request.query_params.get("task_id") or f"hello-{request.state.session_id}"

    store = await FoundryStateStore.get_or_create(CHECKPOINT_STORE)
    try:
        item = await store.get_item(task_id)
    finally:
        await store.aclose()

    if item is None:
        return JSONResponse({"status": "not_started", "task_id": task_id}, status_code=404)

    value = item.value or {}
    done = int(value.get("completed_steps", 0) or 0)
    total = int(value.get("steps", 0) or 0)
    status = "completed" if total and done >= total else "in_progress"
    return JSONResponse(
        {
            "status": status,
            "task_id": task_id,
            "completed_steps": done,
            "total_steps": total,
        }
    )


if __name__ == "__main__":
    app.run()
