"""Minimal HTTP host for the cancellable resilient job — **start, poll, cancel**.

- ``POST /invocations`` with body ``{"name": "...", "steps": N}`` — starts the
  durable job and returns ``202`` with its ``invocation_id``.
- ``GET /invocations/{invocation_id}`` — JSON snapshot of ``status`` and
  ``completed_steps``. Status is one of ``in_progress`` / ``cancelling`` /
  ``cancelled`` / ``completed`` / ``failed``.
- ``POST /invocations/{invocation_id}/cancel`` — request cooperative
  cancellation. Writes a durable cancel marker; the running job notices it before
  its next step and stops with ``status: cancelled``.

Run it::

    pip install -r requirements.txt
    python app.py

Then (use the same ``?agent_session_id=`` on every call so poll/cancel hit the
same session-scoped store)::

    # start a 30-step job (STEP_DELAY defaults to 2s, so ~60s of work)
    curl -s -XPOST -H "Content-Type: application/json" \\
        -d '{"name": "Ada", "steps": 30}' \\
        "http://localhost:8088/invocations?agent_session_id=demo"
    # -> {"status": "started", "invocation_id": "<inv>", "total_steps": 30}

    # poll it — completed_steps climbs while status is "in_progress"
    curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
    # -> {"status": "in_progress", "completed_steps": 4, "total_steps": 30}

    # cancel it mid-run
    curl -s -XPOST "http://localhost:8088/invocations/<inv>/cancel?agent_session_id=demo"
    # -> {"status": "cancelling", "invocation_id": "<inv>"}

    # poll again — the job stopped early
    curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
    # -> {"status": "cancelled", "completed_steps": 4, "total_steps": 30}
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
    from .agent import (
        CANCEL_SUFFIX,
        cancellable_job,
        durable_task_id,
        open_checkpoint_store,
    )
except ImportError:  # allows `python app.py` from inside this directory
    from agent import (
        CANCEL_SUFFIX,
        cancellable_job,
        durable_task_id,
        open_checkpoint_store,
    )

# Resilient tasks (durable execution + crash recovery) are strictly opt-in as of
# azure-ai-agentserver-core 2.1.0b1: the host builds the ``TaskManager`` (and runs
# the recovery scan) ONLY when this switch is on, and it must be set before host
# startup (i.e. at module-import time). Without it, ``cancellable_job.start()``
# raises ``TaskManagerNotInitialized`` and there is no crash recovery.
set_resilient_tasks_enabled(True)

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start the durable job and return immediately (it runs in the background)."""
    try:
        data = json.loads(await request.body() or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        # UnicodeDecodeError: request bytes are not valid UTF-8. Both are
        # malformed-body cases and must be 400, not an internal 500.
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse(
            {"error": "request body must be a JSON object"}, status_code=400
        )
    name = str(data.get("name", "world"))
    # ``steps`` must be a positive integer. Validate the *decoded JSON type* (not
    # via ``int(...)``, which would accept ``True`` or truncate ``2.9``).
    steps = data.get("steps", 10)
    if isinstance(steps, bool) or not isinstance(steps, int):
        return JSONResponse({"error": "steps must be an integer"}, status_code=400)
    if steps <= 0:
        return JSONResponse(
            {"error": "steps must be a positive integer"}, status_code=400
        )

    # Identity: compose the durable task id from user + session + invocation so
    # runs cannot collide or be cross-accessed. session_id/user_id are carried in
    # the input so recovery reopens the same store scope + user partition; call_id
    # is carried so the TaskManager can restore the Foundry call identity for
    # hosted store calls after a crash (recovered tasks have no inbound request).
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    call_id: str = request.state.call_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    # The durable record is the authoritative existence gate — NOT start(). A
    # one-shot task record is deleted on terminal exit (completed/cancelled/
    # failed), so once a job has ended, ``start()`` would NOT conflict and a reused
    # invocation id would spin up a new task against the stale checkpoint/marker.
    # So we gate on an atomic ``create_item``: success => genuinely new job, start
    # it; conflict => the invocation already exists and we return 409 with its
    # current status. Seeding before ``start()`` also makes the invocation visible
    # on every replica immediately (no pre-checkpoint 404 window).
    store = await open_checkpoint_store(session_id, user_id)
    try:
        try:
            await store.create_item(
                task_id,
                {
                    "name": name,
                    "steps": steps,
                    "completed_steps": 0,
                    "status": "in_progress",
                },
            )
        except FoundryStorageConflictError:
            existing = await store.get_item(task_id)
            status = (existing.value.get("status") if existing else None) or "unknown"
            return JSONResponse(
                {
                    "status": status,
                    "invocation_id": invocation_id,
                    "detail": "invocation already exists",
                },
                status_code=409,
            )
    finally:
        await store.aclose()

    try:
        await cancellable_job.start(
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
        # We just created the record, so a conflict here is only a rare
        # concurrent-start race; report it rather than 500ing.
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
    """Return a JSON status snapshot from the durable checkpoint (poll this).

    Status is derived from durable state, so it is correct on any replica and
    after a crash. Terminal states (``completed``/``cancelled``/``failed``) are
    persisted by the task; ``cancelling`` means a cancel was requested but the
    job has not yet reached its next step. A started invocation always has a
    durable record (seeded by the invoke handler), so an absent record means a
    genuinely unknown invocation.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    store = await open_checkpoint_store(session_id, user_id)
    try:
        item = await store.get_item(task_id)
        cancel_marker = await store.get_item(f"{task_id}{CANCEL_SUFFIX}")
    finally:
        await store.aclose()

    if item is None and cancel_marker is None:
        return JSONResponse(
            {"status": "not_found", "invocation_id": invocation_id}, status_code=404
        )

    value = item.value if item else {}
    done = int(value.get("completed_steps", 0) or 0)
    total = int(value.get("steps", 0) or 0)
    persisted = value.get("status")
    if persisted in ("completed", "cancelled", "failed"):
        status = persisted
    elif cancel_marker is not None:
        # Cancel requested; the job has not yet observed it and finalized.
        status = "cancelling"
    else:
        status = "in_progress"
    body = {
        "status": status,
        "invocation_id": invocation_id,
        "completed_steps": done,
        "total_steps": total,
    }
    if status == "failed" and value.get("error"):
        body["error"] = value["error"]
    return JSONResponse(body)


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Request cooperative cancellation of a running job.

    Writes a durable cancel marker the job checks before each step. Refuses to
    persist a marker for an invocation that does not exist (an unknown/arbitrary
    id would otherwise poison a later legitimate start with the same session/id).
    Existence is decided by the durable record seeded at invoke time (visible on
    every replica), not the replica-local ``get_active_run()``.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    store = await open_checkpoint_store(session_id, user_id)
    try:
        if await store.get_item(task_id) is None:
            return JSONResponse(
                {"status": "not_found", "invocation_id": invocation_id},
                status_code=404,
            )
        await store.set_item(f"{task_id}{CANCEL_SUFFIX}", {"cancel": True})
    finally:
        await store.aclose()

    return JSONResponse({"status": "cancelling", "invocation_id": invocation_id})


if __name__ == "__main__":
    app.run()
