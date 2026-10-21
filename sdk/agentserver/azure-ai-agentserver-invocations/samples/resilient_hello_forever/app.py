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

from azure.ai.agentserver.core.storage import FoundryStorageConflictError
from azure.ai.agentserver.core.tasks import (
    TaskConflictError,
    set_resilient_tasks_enabled,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from .agent import (
        STOP_SUFFIX,
        durable_task_id,
        hello_forever,
        open_checkpoint_store,
    )
except ImportError:  # allows `python app.py` from inside this directory
    from agent import (
        STOP_SUFFIX,
        durable_task_id,
        hello_forever,
        open_checkpoint_store,
    )

# Resilient tasks (durable execution + crash recovery) are strictly opt-in as of
# azure-ai-agentserver-core 2.1.0b1: ``AgentServerHost`` builds the
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
    except (json.JSONDecodeError, UnicodeDecodeError):
        # UnicodeDecodeError: request bytes are not valid UTF-8. Both are
        # malformed-body cases and must be 400, not an internal 500.
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse(
            {"error": "request body must be a JSON object"}, status_code=400
        )
    name = str(data.get("name", "world"))

    # Identity for this worker. The invocation id is caller-supplied and a session
    # may serve multiple users, so compose the durable task id from user + session
    # + invocation (see durable_task_id) so workers cannot collide or be
    # cross-accessed. session_id/user_id are carried in the input so recovery
    # reopens the same store scope + user partition; call_id is carried so the
    # TaskManager can restore the Foundry call identity for hosted store calls
    # after a crash (recovered tasks have no inbound request).
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    call_id: str = request.state.call_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    # The durable record is the authoritative existence gate — NOT start(). A
    # one-shot task record is deleted on terminal exit (stop/failure), so once a
    # worker has stopped, ``start()`` would NOT conflict and a reused invocation id
    # would spin up a brand-new task that immediately sees the OLD stop marker and
    # exits — while POST wrongly reported "started". So we gate on an atomic
    # ``create_item``:
    #   * success -> genuinely new worker; schedule it.
    #   * conflict + TERMINAL (stop marker present, or status == "failed") ->
    #     idempotent; return 409 (never re-run).
    #   * conflict + NONTERMINAL ("running") -> the record exists but may be an
    #     ORPHAN (an earlier attempt seeded it then crashed before the worker was
    #     durably scheduled). Fall through and (re-)schedule idempotently —
    #     ``start()`` recovers the orphan; ``TaskConflictError`` means a worker is
    #     already running. Seeding before ``start()`` also makes the invocation
    #     visible on every replica immediately (no pre-checkpoint 404 window).
    seeded_now = False
    store = await open_checkpoint_store(session_id, user_id)
    try:
        try:
            await store.create_item(
                task_id, {"name": name, "iterations": 0, "status": "running"}
            )
            seeded_now = True
        except FoundryStorageConflictError:
            existing = await store.get_item(task_id)
            stop_marker = await store.get_item(f"{task_id}{STOP_SUFFIX}")
            evalue = existing.value if existing else {}
            status = evalue.get("status") or "running"
            if stop_marker is not None:
                status = "stopped"
            if stop_marker is not None or status == "failed":
                return JSONResponse(
                    {
                        "status": status,
                        "invocation_id": invocation_id,
                        "detail": "invocation already exists",
                    },
                    status_code=409,
                )
            # Nonterminal ("running"): fall through to (re-)schedule idempotently.
            # Reuse the PERSISTED name, not this retry's body, so an orphan retry
            # cannot mutate the identity recorded by the original invocation.
            name = str(evalue.get("name", name))
    finally:
        await store.aclose()

    try:
        await hello_forever.start(
            task_id=task_id,
            input={
                "name": name,
                "session_id": session_id,
                "user_id": user_id,
                "call_id": call_id,
            },
        )
    except TaskConflictError:
        # A worker is already scheduled/running for this id — idempotent.
        return JSONResponse(
            {"status": "already_running", "invocation_id": invocation_id},
            status_code=409,
        )
    except Exception:
        # Non-conflict scheduling failure. If we seeded the record this request,
        # remove it so a retry can start cleanly rather than being wedged behind a
        # permanent ``running`` record with no worker to recover. (An ambiguous
        # remote accept is still safe: a retry re-seeds and ``start()`` raises
        # TaskConflictError, handled as "already running".)
        if seeded_now:
            try:
                cleanup = await open_checkpoint_store(session_id, user_id)
                try:
                    await cleanup.delete_item(task_id)
                finally:
                    await cleanup.aclose()
            except Exception:  # noqa: BLE001 — best-effort compensation
                pass
        raise

    return JSONResponse(
        {"status": "started", "invocation_id": invocation_id}, status_code=202
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Report whether the worker is running, stopped, or failed.

    Status is derived from **durable state**, not process-local run ownership: an
    indefinite worker keeps running (possibly on a *different* replica) until it
    is explicitly stopped, so ``get_active_run()`` returning ``None`` on the
    polled replica means nothing. The invoke handler seeds an initial durable
    record, so a started invocation is visible on every replica immediately (no
    pre-checkpoint 404 window). Terminal state is durable: the stop marker means
    ``stopped``; the worker persists ``status: failed`` on an unhandled exception
    (its one-shot record is deleted on terminal exit, so without that a crashed
    worker would report ``running`` forever). Absence of both the record and the
    marker means the invocation is genuinely unknown.
    """
    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    user_id: str = request.state.user_id
    task_id = durable_task_id(session_id, invocation_id, user_id)

    store = await open_checkpoint_store(session_id, user_id)
    try:
        item = await store.get_item(task_id)
        stop_marker = await store.get_item(f"{task_id}{STOP_SUFFIX}")
    finally:
        await store.aclose()

    if item is None and stop_marker is None:
        # No durable record and no stop marker: genuinely unknown invocation.
        # (A started invocation always has a record from the invoke handler.)
        return JSONResponse(
            {"status": "not_found", "invocation_id": invocation_id},
            status_code=404,
        )

    value = item.value if item else {}
    iterations = int(value.get("iterations", 0) or 0)
    if stop_marker is not None:
        status = "stopped"
    elif value.get("status") == "failed":
        status = "failed"
    else:
        status = "running"
    body = {
        "status": status,
        "invocation_id": invocation_id,
        "iterations": iterations,
    }
    if status == "failed" and value.get("error"):
        body["error"] = value["error"]
    return JSONResponse(body)


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Stop the forever worker.

    Refuses to persist a stop marker for an invocation that does not exist:
    otherwise cancelling an arbitrary caller-chosen id would make GET report it
    ``stopped`` and would poison a *later* legitimate start with the same
    session/id (the worker would see the stale marker and exit immediately).
    Existence is decided by the **durable record** seeded at invoke time (visible
    on every replica), not the replica-local ``get_active_run()``. The worker
    re-reads the stop marker at the top of every iteration, so it stops within one
    tick without any in-process wake signal.
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
        await store.set_item(f"{task_id}{STOP_SUFFIX}", {"stop": True})
    finally:
        await store.aclose()

    return JSONResponse({"status": "cancelling", "invocation_id": invocation_id})


if __name__ == "__main__":
    app.run()
