# Copyright (c) Microsoft. All rights reserved.

"""HTTP host for the resilient research agent.

This file is minimal plumbing. The resilience + steering logic is in ``agent.py``.

Streaming is wired through the SDK ``streams`` registry: at startup
we pick the **file-backed replay** backing (events persist to disk so
they survive a crash + container restart). The POST handler reserves
the per-turn stream id (``invocation_id``) BEFORE starting the task so
the GET handler can subscribe deterministically. The handler in
``agent.py`` emits to the same id; events on the SSE wire carry the
emitted ``sequence_number`` as the SSE ``id:`` field, so a reconnect
with ``?last_event_id=N`` skips events the client already received.

Routes (all platform-managed — only ``/invocations*`` is reachable
through the Foundry endpoint proxy):
  * ``POST /invocations``                       — fire-and-forget dispatch (or
                                                   steering input on an in-progress run);
                                                   special: ``{"message": "crash"}``
                                                   when ``DEMO_MODE=1`` forces a process
                                                   exit so the platform nanny restarts us
  * ``GET  /invocations/{id}?last_event_id=N``  — SSE stream of the active run
  * ``POST /invocations/{id}/cancel``           — operator cancel
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core.streaming import (
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.invocations import InvocationAgentServerHost

from agent import deep_research

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# --- Streams bootstrap (run once at module import) --------------------------

# Per-turn streams persist to disk so they survive a container crash +
# restart. ``cursor_fn`` reads the agent's natural sequence number so
# ``?last_event_id=N`` reconnects skip already-delivered events.
# ``ttl_seconds=600`` bounds disk usage: once a stream is closed and
# all its events have aged out, the registry destroys it and removes
# the file.
_STREAM_DIR = Path.home() / ".agentserver-tasks" / "_streams"
_STREAM_DIR.mkdir(parents=True, exist_ok=True)

streams.use_file_backed_replay(
    storage_dir=_STREAM_DIR,
    cursor_fn=lambda ev: ev["sequence_number"],
    ttl_seconds=600,
)


app = InvocationAgentServerHost()


# --- Invocation handlers ---------------------------------------------------


@app.invoke_handler
async def handle_invoke(request: Request) -> Response:
    """Dispatch a research task (fire-and-forget).

    Input shape: ``{"message": "<topic>"}``.

    Two special behaviors driven by the request body:

    * ``{"message": "crash"}`` (when the container has ``DEMO_MODE=1``) forces
      ``os._exit(137)`` shortly after returning ``202``. The platform's nanny
      worker brings the container back within ~1 min on its own — no new
      client ingress required — and the resilient task auto-resumes from its
      last checkpoint.

    * Any other ``{"message": "<topic>"}`` dispatches a normal research run.
      If a steerable run is already in progress on this session, the input is
      queued as a steering input — the agent winds down the current turn at
      the next checkpoint and re-enters with the new topic.
    """
    body = await request.body()
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}
    topic = str(data.get("message") or "").strip()
    if not topic:
        return JSONResponse({"error": "Provide a 'message' field"}, status_code=400)

    # Demo-only crash trigger.
    if topic.lower() in ("crash", "kill", "💥") and os.environ.get("DEMO_MODE") == "1":
        logger.critical("CRASH triggered via /invocations message=%r — exiting in 300ms", topic)

        async def _crash() -> None:
            await asyncio.sleep(0.3)
            os._exit(137)

        asyncio.get_event_loop().create_task(_crash())
        return JSONResponse(
            {
                "status": "crashing",
                "message": (
                    "Process will exit. The platform's nanny worker brings the "
                    "container back within ~1 min on its own (no new ingress "
                    "required) and the resilient task auto-resumes from its last "
                    "checkpoint."
                ),
            },
            status_code=202,
        )

    invocation_id: str = request.state.invocation_id
    session_id: str = request.state.session_id
    # ONE resilient task per session so steering finds the active run.
    # invocation_id labels THIS turn; session_id labels the long-lived task.
    task_id = session_id
    logger.info(
        "POST handler: session_id=%r task_id=%r invocation_id=%r topic=%r", session_id, task_id, invocation_id, topic
    )

    # Reserve the per-turn stream id BEFORE starting the task. This
    # guarantees a GET that races the POST sees the stream (rather than
    # a 404 NotFound). The file-backed replay backing means we don't
    # need to wait for a subscriber before the handler starts emitting.
    await streams.get_or_create(invocation_id)

    # Steering is transparent to callers: for a steerable=True chain,
    # multi_turn_task.start() queues the input on the in-progress chain's
    # steering queue WITHOUT raising. The agent's currently-running turn
    # observes ctx.cancel.is_set(), winds down at its next checkpoint, and
    # the framework re-enters the body with the queued input as
    # ctx.input — at which point the new turn streams its events to
    # the per-turn invocation_id stream reserved above. No status
    # branching is needed here.
    #
    # invocation_id is also the per-turn ``input_id`` — the framework
    # records it as the chain's last-accepted input id (see
    # ``payload["_last_input_id"]``) and uses it for the multi-turn
    # ``get_active_run(task_id, input_id)`` match.
    await deep_research.start(
        task_id=task_id,
        input={"topic": topic, "invocation_id": invocation_id},
        input_id=invocation_id,
    )

    return JSONResponse(
        {
            "status": "started",
            "invocation_id": invocation_id,
            "session_id": session_id,
        },
        status_code=202,
    )


@app.get_invocation_handler
async def handle_get(request: Request) -> Response:
    """Stream SSE from the per-invocation stream.

    The platform routes ``GET /invocations/{id}`` to this container based on
    the invocation-to-session mapping set up by the original POST. Clients
    can pass ``?last_event_id=N`` to skip events they've already seen on a
    reconnect — we forward this to ``stream.subscribe(after=N)`` which
    skips events whose sequence_number ≤ N (whether they're being served
    from in-memory live, from on-disk replay, or from a rehydrated stream
    after a crash).

    HTTP mapping:
      - 404 if the invocation id was never seen
        (``EventStreamNotFoundError``).
      - 410 if the stream was destroyed (TTL eviction or explicit
        ``streams.delete``) (``EventStreamNotFoundError``).
    """
    invocation_id = request.state.invocation_id

    last_event_id = request.query_params.get("last_event_id", "")
    skip_count = int(last_event_id) if last_event_id.isdigit() else 0
    logger.info("GET handler: invocation_id=%r skip=%d", invocation_id, skip_count)

    try:
        stream = await streams.get(invocation_id)
    except EventStreamNotFoundError:
        return JSONResponse(
            {"status": "not_found", "message": "No stream for this invocation id."},
            status_code=404,
        )
    except EventStreamNotFoundError:
        return JSONResponse(
            {"status": "gone", "message": "Stream for this invocation id has been destroyed."},
            status_code=410,
        )

    async def sse_stream():
        try:
            async for event in stream.subscribe(after=skip_count or None):
                seq = event.get("sequence_number")
                yield f"id: {seq}\ndata: {json.dumps(event)}\n\n"
        except EventStreamNotFoundError:
            # Stream destroyed while we were attached (TTL eviction or
            # explicit delete). Tell the client we're done.
            yield (f"event: gone\ndata: " + json.dumps({"type": "gone", "invocation_id": invocation_id}) + "\n\n")

    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.cancel_invocation_handler
async def handle_cancel(request: Request) -> Response:
    """Cancel the running research task.

    Cancel applies to the per-session resilient task (task_id == session_id).
    The handler observes ``ctx.cancel.is_set()`` and runs its
    cooperative wind-down at the next checkpoint, which closes the
    per-turn stream before suspending.
    """
    invocation_id = request.state.invocation_id
    # The framework resolves session_id from the platform env var
    # ``FOUNDRY_AGENT_SESSION_ID`` (or a caller-supplied
    # ``agent_session_id`` query param override) and stamps it on
    # ``request.state.session_id``. No local fallback needed.
    session_id = request.state.session_id
    task_id = session_id  # one task per session — match POST handler
    logger.info("CANCEL handler: invocation_id=%r task_id=%r", invocation_id, task_id)

    # ``input_id == invocation_id`` per the POST handler's start() call.
    # MultiTurnTask.get_active_run requires the input_id of the current
    # turn so the framework can verify the caller is targeting the
    # in-flight turn and not a stale one.
    run = await deep_research.get_active_run(task_id, invocation_id)
    if run is None:
        return JSONResponse({"status": "not_found", "message": "No active task to cancel."})

    await run.cancel()
    return JSONResponse({"status": "cancelled", "message": "Task cancellation requested."})


if __name__ == "__main__":
    app.run()
