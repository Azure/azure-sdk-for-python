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

Then (use the invocation_id from the POST response / X-Agent-Invocation-Id)::

    # start the forever worker
    curl -s -XPOST -H "Content-Type: application/json" \\
        -d '{"name": "Ada"}' http://localhost:8088/invocations
    # -> {"status": "started", "invocation_id": "<inv>"}

    # poll it — iterations keep climbing, status stays "running"
    curl -s "http://localhost:8088/invocations/<inv>"
    # -> {"status": "running", "iterations": 12}

    # stop it
    curl -s -XPOST "http://localhost:8088/invocations/<inv>/cancel"
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
    from .agent import CHECKPOINT_STORE, STOP_SUFFIX, hello_forever
except ImportError:  # allows `python app.py` from inside this directory
    from agent import CHECKPOINT_STORE, STOP_SUFFIX, hello_forever

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
        data = {}
    name = str(data.get("name", "world"))

    # Key the worker by this turn's invocation id (the platform-defined identity
    # that GET/cancel address via the {invocation_id} path).
    invocation_id: str = request.state.invocation_id
    await hello_forever.start(task_id=invocation_id, input={"name": name})

    return JSONResponse(
        {"status": "started", "invocation_id": invocation_id}, status_code=202
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Report whether the worker is running and its current iteration count."""
    invocation_id: str = request.state.invocation_id

    run = await hello_forever.get_active_run(invocation_id)
    store = await FoundryStateStore.get_or_create(CHECKPOINT_STORE)
    try:
        item = await store.get_item(invocation_id)
    finally:
        await store.aclose()

    if item is None and run is None:
        return JSONResponse(
            {"status": "not_found", "invocation_id": invocation_id}, status_code=404
        )

    iterations = int((item.value.get("iterations", 0) if item else 0) or 0)
    return JSONResponse(
        {
            "status": "running" if run is not None else "stopped",
            "invocation_id": invocation_id,
            "iterations": iterations,
        }
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Stop the forever worker.

    Writes a durable stop marker (which the worker checks — robust even after the
    per-turn watchdog fires and across recovery), then signals the running turn
    to wake promptly from its sleep.
    """
    invocation_id: str = request.state.invocation_id

    store = await FoundryStateStore.get_or_create(CHECKPOINT_STORE)
    try:
        await store.set_item(f"{invocation_id}{STOP_SUFFIX}", {"stop": True})
    finally:
        await store.aclose()

    run = await hello_forever.get_active_run(invocation_id)
    if run is not None:
        await run.cancel()  # wake the worker so it notices the stop marker promptly
    return JSONResponse({"status": "cancelling", "invocation_id": invocation_id})


if __name__ == "__main__":
    app.run()
