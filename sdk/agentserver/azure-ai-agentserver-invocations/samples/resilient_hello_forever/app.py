"""Minimal HTTP host for the *indefinite* "hello forever" resilient agent.

No streaming — **start, poll, and cancel**:

- ``POST /invocations`` with body ``{"name": "..."}`` — starts the durable
  worker and returns ``202`` with its ``invocation_id``. The worker runs forever
  in the background until cancelled.
- ``GET /invocations/{invocation_id}`` — JSON snapshot: whether the worker is
  ``running`` and its current ``iterations`` count.
- ``POST /invocations/{invocation_id}/cancel`` — stop the worker.

Run it::

    pip install -r requirements.txt
    python app.py

Then (use the invocation_id from the POST response / X-Agent-Invocation-Id, and
the same ``?agent_session_id=`` on every call so poll/cancel hit the same
session-scoped store)::

    # start the forever worker
    curl -s -XPOST -H "Content-Type: application/json" \\
        -d '{"name": "Ada"}' \\
        "http://localhost:8088/invocations?agent_session_id=demo"
    # -> {"status": "started", "invocation_id": "<inv>"}

    # poll it — iterations keep climbing, status stays "running"
    curl -s "http://localhost:8088/invocations/<inv>?agent_session_id=demo"
    # -> {"status": "running", "iterations": 12}

    # stop it
    curl -s -XPOST "http://localhost:8088/invocations/<inv>/cancel?agent_session_id=demo"
    # -> {"status": "cancelling", "invocation_id": "<inv>"}
"""

from __future__ import annotations

import json

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import (
        STOP_SUFFIX,
        checkpoint_store_name,
        durable_task_id,
        hello_forever,
    )
except ImportError:  # allows `python app.py` from inside this directory
    from agent import (
        STOP_SUFFIX,
        checkpoint_store_name,
        durable_task_id,
        hello_forever,
    )

# Resilient tasks (durable execution + crash recovery) are strictly opt-in as of
# azure-ai-agentserver-core 2.2.0b1: ``AgentServerHost`` builds the
# ``TaskManager`` ONLY when this switch is on, and it must be set before host
# startup (i.e. at module-import time). Without it, ``hello_forever.start()``
# raises ``TaskManagerNotInitialized`` and there is no crash recovery — which
# would defeat the purpose of a long-running agent.
set_resilient_tasks_enabled(True)

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Start the forever worker and return immediately (it runs in the background)."""
    try:
        data = json.loads(await request.body() or b"{}")
    except json.JSONDecodeError:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse(
            {"error": "request body must be a JSON object"}, status_code=400
        )
    name = str(data.get("name", "world"))

    # The invocations protocol addresses the run by the {invocation_id} path, but
    # that id is caller-supplied and can repeat across sessions; compose it with
    # the session id for the durable task id so workers cannot collide. The
    # session id is also carried in the input so recovery uses the same scope.
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = durable_task_id(session_id, invocation_id)
    await hello_forever.start(
        task_id=task_id, input={"name": name, "session_id": session_id}
    )

    return JSONResponse(
        {"status": "started", "invocation_id": invocation_id}, status_code=202
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Report whether the worker is running and its current iteration count.

    Status is derived from the **durable stop marker**, not from process-local
    run ownership: an indefinite worker keeps running (possibly on a *different*
    replica) until it is explicitly stopped, so ``get_active_run()`` returning
    ``None`` on the polled replica does not mean the worker has stopped. The stop
    marker is written by the cancel handler and survives crashes and recovery, so
    every replica agrees on the terminal state. ``get_active_run()`` is consulted
    only to disambiguate the brief window *before the first checkpoint* (both the
    checkpoint and marker are still absent) from a genuinely unknown invocation.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = durable_task_id(session_id, invocation_id)

    store = await FoundryStateStore.get_or_create(
        checkpoint_store_name(session_id), item_ttl_seconds=-1
    )
    try:
        item = await store.get_item(task_id)
        stop_marker = await store.get_item(f"{task_id}{STOP_SUFFIX}")
    finally:
        await store.aclose()

    if item is None and stop_marker is None:
        # No checkpoint and no stop marker. The worker may have just started and
        # not yet written its first checkpoint, so distinguish "running at zero"
        # (this replica owns an active run) from a genuinely unknown invocation.
        run = await hello_forever.get_active_run(task_id)
        if run is None:
            return JSONResponse(
                {"status": "not_found", "invocation_id": invocation_id},
                status_code=404,
            )
        return JSONResponse(
            {"status": "running", "invocation_id": invocation_id, "iterations": 0}
        )

    iterations = int((item.value.get("iterations", 0) if item else 0) or 0)
    return JSONResponse(
        {
            "status": "stopped" if stop_marker is not None else "running",
            "invocation_id": invocation_id,
            "iterations": iterations,
        }
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Stop the forever worker.

    Refuses to persist a stop marker for an invocation that does not exist:
    otherwise cancelling an arbitrary caller-chosen id would make GET report it
    ``stopped`` and would poison a *later* legitimate start with the same
    session/id (the worker would see the stale marker and exit immediately). An
    invocation is considered to exist if it has an active run on this replica or
    a durable checkpoint (written on any replica). Only then do we write the
    marker and wake the running turn.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    task_id = durable_task_id(session_id, invocation_id)

    run = await hello_forever.get_active_run(task_id)

    store = await FoundryStateStore.get_or_create(
        checkpoint_store_name(session_id), item_ttl_seconds=-1
    )
    try:
        exists = await store.get_item(task_id) is not None
        if not exists and run is None:
            return JSONResponse(
                {"status": "not_found", "invocation_id": invocation_id},
                status_code=404,
            )
        await store.set_item(f"{task_id}{STOP_SUFFIX}", {"stop": True})
    finally:
        await store.aclose()

    if run is not None:
        await run.cancel()  # wake the worker so it notices the stop marker promptly
    return JSONResponse({"status": "cancelling", "invocation_id": invocation_id})


if __name__ == "__main__":
    app.run()
