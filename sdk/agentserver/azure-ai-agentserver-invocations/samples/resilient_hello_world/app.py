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

from azure.ai.agentserver.core.storage import FoundryStorageConflictError
from azure.ai.agentserver.core.tasks import (
    TaskConflictError,
    set_resilient_tasks_enabled,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import durable_task_id, hello_world, open_checkpoint_store
except ImportError:  # allows `python app.py` from inside this directory
    from agent import durable_task_id, hello_world, open_checkpoint_store

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
    # ``steps`` must be a positive integer. Validate the *decoded JSON type* (not
    # via ``int(...)``, which would accept ``True`` or silently truncate ``2.9``).
    # A non-positive count writes no checkpoint, so the accepted invocation would
    # then poll as 404.
    steps = data.get("steps", 10)
    if isinstance(steps, bool) or not isinstance(steps, int):
        return JSONResponse(
            {"error": "steps must be an integer"}, status_code=400
        )
    if steps <= 0:
        return JSONResponse(
            {"error": "steps must be a positive integer"}, status_code=400
        )

    # Identity for this run. The invocation id is caller-supplied and a session
    # may serve multiple users, so compose the durable task id from user +
    # session + invocation (see durable_task_id) so runs cannot collide or be
    # cross-accessed. session_id/user_id are carried in the input so recovery
    # reopens the same store scope + user partition; call_id is carried so the
    # TaskManager can restore the Foundry call identity for hosted store calls
    # after a crash (recovered tasks have no inbound request).
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    call_id: str = request.state.call_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    # Persist an initial durable checkpoint BEFORE starting the task so the
    # invocation is visible on every replica immediately. Without it a poll routed
    # to a different replica during the pre-first-checkpoint window sees
    # get_active_run()==None (the live lease may be owned elsewhere) and would
    # wrongly 404. Use create_item (atomic create) rather than a non-atomic
    # get-then-set: concurrent retries otherwise both see "absent" and a delayed
    # set_item could clobber a checkpoint the worker has already advanced.
    store = await open_checkpoint_store(session_id, user_id)
    try:
        await store.create_item(
            task_id, {"name": name, "steps": steps, "completed_steps": 0}
        )
    except FoundryStorageConflictError:
        pass  # already seeded by a concurrent request or a previous attempt
    finally:
        await store.aclose()

    # start() schedules the task on the TaskManager and returns right away — the
    # work is NOT tied to this HTTP request's lifetime.
    try:
        await hello_world.start(
            task_id=task_id,
            input={
                "name": name,
                "steps": steps,
                "session_id": session_id,
                "user_id": user_id,
                "call_id": call_id,
            },
        )
    except TaskConflictError:
        # The invocation id is caller-supplied and may be retried; a task already
        # in progress (or completed) for this session+id is not an error — report
        # the existing run rather than 500ing.
        return JSONResponse(
            {"status": "already_started", "invocation_id": invocation_id},
            status_code=409,
        )

    return JSONResponse(
        {"status": "started", "invocation_id": invocation_id, "total_steps": steps},
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Return a JSON status snapshot from the durable checkpoint (poll this)."""
    # The invocations protocol addresses the run by the {invocation_id} path
    # segment; the durable task id is composed from user + session + invocation so
    # a poll only ever resolves this user's own run in this session.
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    store = await open_checkpoint_store(session_id, user_id)
    try:
        item = await store.get_item(task_id)
    finally:
        await store.aclose()

    if item is None:
        # A started invocation always has a durable record (seeded by the invoke
        # handler), so an absent record means a genuinely unknown invocation.
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
